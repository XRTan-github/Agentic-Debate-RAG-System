from Helper.Neo4j_tools import run_similarity_query,build_composition_summary,domain_matched_search
from Helper.checkpoint_manager import update_checkpoint
from LLM_agents.RAG_summary import RAG_summary

# ---------- Full pipeline ----------
def initial_process_rag(checkpoint,target_n):

    common_info = checkpoint["task_output"]["common_context"]
    variants = checkpoint["task_output"]["variants"]
    output_expert = []
    output_rag = []
    rag_raw = {}
    rag_summary = {}

    for variant in variants:
        agent_name = variant.get("name")
        agent_type = variant.get("type")
        print(f"\n--- Agent: {agent_name}, type: {agent_type}")

        tags = [variant] + common_info
        output_expert.append(agent_name)
        
        topic_tags = [t["name"] for t in tags if t.get("type") != "composition"]
        topic_txt = ", ".join(topic_tags)
        all_text_blocks = []

        for com in tags:
            if com.get("type") == "composition":
                composition_key = com["composition_key"]
                print(f"\n--- Running similarity search for: {composition_key}")

                comp_top = run_similarity_query(composition_key, target_n=target_n)
                for r in comp_top:
                    similar_comp = r["similar_composition"]
                    print(f"\n--- Composition-similar: {similar_comp}")
                    info = build_composition_summary(similar_comp)
                    if info:
                        all_text_blocks.append(info)
                
                domain_top = domain_matched_search(composition_key, topic_txt, target_n=target_n)
                domain_top = [r for r in domain_top if r["similar_composition"] not in 
                               [x["similar_composition"] for x in comp_top]]
                for r in domain_top:
                    similar_comp = r["similar_composition"]
                    print(f"\n--- Composition-similar and same-domain: {similar_comp}")
                    info = build_composition_summary(similar_comp)
                    if info:
                        all_text_blocks.append(info)
        rag_raw[agent_name] = all_text_blocks
        input_text = "\n\n".join(all_text_blocks)
        max_tokens = 10000
        reply = RAG_summary(topic_txt, input_text, max_tokens)
        print("\n=== RAG Summary ===\n", reply)
        rag_summary[agent_name] = reply
        output_rag.append(reply)
    checkpoint["rag_raw"] = rag_raw
    checkpoint["rag_summary"] = rag_summary
    update_checkpoint(checkpoint["question"], checkpoint)
    return output_expert, output_rag