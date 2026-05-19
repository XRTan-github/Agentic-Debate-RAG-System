from Helper.checkpoint_manager import update_checkpoint
from LLM_agents.domain_expert import domain_agent
from LLM_agents.moderator import moderator_agent
from LLM_agents.critic import critic_agent
from LLM_agents.theory_agent import theory_agent
from LLM_agents.experiment_agent import experiment_suggestion_agent
# ================================================
#  CHECKPOINT HELPERS
# ================================================
def ensure_debate_storage(cp):
    cp.setdefault("debate", {})

def ensure_round(cp, r):
    r = str(r)
    ensure_debate_storage(cp)
    rd = cp["debate"].setdefault(r, {})
    rd.setdefault("domain_outputs", {})
    return rd

def is_domain_done(cp, r, domain):
    r = str(r)
    return (
        "debate" in cp and
        r in cp["debate"] and
        domain in cp["debate"][r].get("domain_outputs", {})
    )

# ================================================
def cached_call(question,cp, path, fn):
    """
    path = ("debate", "1", "domain_outputs", "Oxidation")
    """
    node = cp
    for p in path[:-1]:
        node = node.setdefault(p, {})
    key = path[-1]

    # Already exists
    if key in node:
        print(f"\n🔁 Using cache: {path}")
        return node[key]

    # Generate
    val = fn()
    node[key] = val
    update_checkpoint(question,cp)   
    return val
# ================================================
def domain_agent_cached(domain, question, evid, mem, crit_mem, cp, r):
    ensure_round(cp, r)
    path = ("debate", str(r), "domain_outputs", domain)
    return cached_call(question,cp, path, lambda: domain_agent(domain, question, evid, mem, crit_mem))

def moderator_cached(outputs, question, cp, r):
    ensure_round(cp, r)
    path = ("debate", str(r), "moderator")
    return cached_call(question,cp, path, lambda: moderator_agent(outputs, question))

def critic_cached(summary,rag,previous_critiques, question, cp, r):
    ensure_round(cp, r)
    path = ("debate", str(r), "critic")
    return cached_call(question,cp, path, lambda: critic_agent(summary, rag,previous_critiques))

def final_theory_cached(summary, question, cp, r):
    path = ("final_theory",)
    return cached_call(question,cp, path, lambda: theory_agent(summary))

def experiment_cached(theory, question, cp, r):
    path = ("experiment_suggestion",)
    return cached_call(question,cp, path, lambda: experiment_suggestion_agent(theory))

def collect_domain_arguments(cp, r, current_domain):
    r = r-1
    r = str(r)
    if "debate" not in cp or r not in cp["debate"]:
        return ""
    outputs = cp["debate"][r].get("domain_outputs", {})
    blocks = []

    # 1) Add this domain's previous argument first (if exists)
    if current_domain in outputs:
        blocks.append(
            "=== Your previous round argument ===\n"
            f"{outputs[current_domain]}"
        )
    else:
        blocks.append(
            "=== Your previous round argument ===\n(No previous argument found)"
        )

    # 2) Add other domain arguments
    for dom, txt in outputs.items():
        if dom == current_domain:
            continue
        blocks.append(
            f"=== Other domain expert: {dom} ===\n{dom} Expert argue that:{txt}"
        )
    return "\n\n".join(blocks)