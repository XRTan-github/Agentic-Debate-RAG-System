import re
from Helper.general_tools import call_llm
from config.llm_config import expert_config_list,Moderator_Agent_llm_config,api
# =======================================================================================
# Moderator Agent
# =========================
def moderator_agent(agents_output, question, config_list=expert_config_list, llm_config=Moderator_Agent_llm_config,api=api):
    combined = "\n\n".join(
        [f"=== {a['domain'].upper()} EXPERT ===\n{a['response']}" 
         for a in agents_output])

    prompt = f"""
    You are the Moderator.

    Your responsibility is to perform a *rigorous scientific synthesis* from multiple domain experts.

    Your tasks:
    1. Identify **points of agreement** across experts.
    2. Identify **points of disagreement, contradiction, or missing links**.
    3. Highlight **where mechanisms align, conflict, or require clarification**.
    4. Produce a **mechanistically consistent synthesis** using ONLY information from the experts.
    5. Absolutely NO new mechanisms, external data, invented concepts, or creative speculation.

    Your goal is to summary the debate, not to add new content.

    **Experts' Arguments**:
    {combined}

    Produce a synthesis with three labeled sections:
    - AGREEMENTS:
    - DISAGREEMENTS / CONFLICTS:
    - INTEGRATED SYNTHESIS:

    The synthesis must be concise, fully grounded in expert arguments, and strictly non-creative.
    """
##############################################################################
#Respond only with JSON.
    print("📌 === LLM Prompt ===")
    print(f"Prompt Size: {len(prompt)}")
    print("📌====================")
    print(f"Full Prompt: {prompt}")
##############################################################################
    summary = call_llm(prompt, api, config_list, llm_config)
    text = summary.choices[0].message.content.strip()
    print("✔=== LLM Response ===")
    print(f"Response Size: {len(text)}")
    print("✔====================")
    print(f"Full Response: {text}")
    return text