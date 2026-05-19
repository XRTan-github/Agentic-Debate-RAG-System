from rapidfuzz import fuzz
from Helper.general_tools import compkey_to_vector

from neo4j import GraphDatabase
from config.neo4j_config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def run_similarity_query(composition_key, driver=driver, target_n=30):
    query_vec = compkey_to_vector(composition_key)
    query ="""
    MATCH (other:Sample)-[:HAS_SAMPLE]-(p:Paper)
    WHERE other.embedding IS NOT NULL

    UNWIND p.domain_tags AS tag   // flatten list

    WITH other,
        collect(DISTINCT tag) AS all_tags,   // remove duplicates
        $query_vec AS query_vec
    WITH other, all_tags,
        reduce(acc = 0.0, i IN range(0, size(query_vec)-1) |
            acc + (query_vec[i] - coalesce(other.embedding[i], 0.0))^2
        ) AS euclidean_distance
    ORDER BY euclidean_distance ASC
    LIMIT $target_n

    RETURN 
        other.composition_key AS similar_composition,
        all_tags AS domain_tags,        // final flattened list
        euclidean_distance,
        other
    """
    with driver.session() as session:
        result = session.run(query, {"query_vec": query_vec, "target_n": target_n})
        return result.data()

# ---------- Filter by domain ----------
def filter_domain_matched(similarity_results, agent_topic):
    matched = []
    for r in similarity_results:
        paper_domains = r.get("domain_tags", [])
        for domain in paper_domains:
            for word in agent_topic.split():
                if fuzz.ratio(word.lower(), domain.lower()) >= 70:
                    matched.append(r)
                    break
            else:
                continue
            break
    return matched

# ---------- Dynamic expanding search ----------
def domain_matched_search(composition_key, agent_topic, target_n=30,
                          initial_n=20, max_n=1000):
    # top_n = initial_n
    domain_matched = []
    
    while initial_n <= max_n:
        full_topN = run_similarity_query(composition_key, target_n=initial_n)
        domain_matched = filter_domain_matched(full_topN, agent_topic)

        check =[]
        for r in full_topN:
            paper_domains = r.get("domain_tags", [])
            check.append(paper_domains)
        print(f"\nChecking domain similarity between input agent topic{agent_topic} and search paper domain tag{check}")

        if len(domain_matched) >= target_n:
            return domain_matched[:target_n]

        initial_n *= 2

    return domain_matched  # may be <3 if DB exhausted

# ---------- Extract nodes and mechanism info ----------
def build_composition_summary(composition_key,driver=driver):
    with driver.session() as session:
        node_query = """
        MATCH (s:Sample {composition_key: $comp})
        MATCH (s)-[:HAS_NODE]->(n:Node)
        RETURN n.id AS id, n.type AS type, n.description AS description
        """
        nodes = session.run(node_query, {"comp": composition_key}).data()
        
        mech_query = """
        MATCH (s:Sample {composition_key: $comp})
        MATCH (s)-[:HAS_NODE]->(n:Node)
        OPTIONAL MATCH (n)-[r:VIA_MECHANISM]->(m:Node)
        WHERE m.composition_key = $comp
        RETURN 
            n.id AS from_id,
            n.type AS from_type,
            n.description AS from_description,
            m.id AS to_id,
            m.type AS to_type,
            m.description AS to_description,
            r.description AS mechanism
        """
        relations = session.run(mech_query, {"comp": composition_key}).data()

    node_lines = [f"{n['type']} {n['description']}" for n in nodes]
    node_summary = ", ".join(node_lines)

    mech_lines = []
    for r in relations:
        if r["to_id"] is None:
            continue
        mech_lines.append(
            f"from {r['from_type']} {r['from_description']} "
            f"connected to {r['to_type']} {r['to_description']} "
            f"because of mechanism '{r['mechanism']}'"
        )

    mech_summary = "\n".join(mech_lines) if mech_lines else "No mechanism links found."

    final_text = f"Composition {composition_key} has {node_summary}.\n\nAnd mechanism links:\n{mech_summary}"
    return final_text

