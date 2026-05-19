import re
from Helper.general_tools import call_llm
from config.llm_config import expert_config_list,Critic_Agent_llm_config,api
# =======================================================================================
# Critic Agent
# =========================
def critic_agent(summary,rag, previous_critiques, config_list=expert_config_list, llm_config=Critic_Agent_llm_config,api=api):
    
    previous_critiques_context  = f"\nIn prior rounds, you identified the following issues: \n{previous_critiques}" if previous_critiques else ""

    prompt = f"""
    You are a scientific critic.
    {previous_critiques_context}

    Your task is to rigorously evaluate the **Moderator Summary** against the **Ground Truth**.

    The Moderator Summary contains:
    - AGREEMENTS
    - DISAGREEMENTS / CONFLICTS
    - INTEGRATED SYNTHESIS

    Instructions:
    1. Focus only on issues that have not yet been resolved or already marked as inherently ambiguous.
    2. For each section, check for:
        - **Accuracy**: Does it correctly reflect the Ground Truth?
        - **Completeness**: Are all major expert arguments represented?
        - **Logical consistency**: No contradictions or unsupported inferences.
        - **Groundedness**: Every claim must be traceable to the Ground Truth.
    3. For solvable issues, suggest **specific, actionable corrections**.
    4. For issues that are inherently ambiguous or unfixable (previously flagged or structurally impossible):
        - Clearly label them in your response as **inherently ambiguous**.
        - Do not repeatedly raise them in future rounds.
    5. Only approve the summary if:
        - All critical issues are resolved, or
        - Remaining issues are persistent issue or inherently ambiguous (use **AGREE TO DISAGREE**).

    DO NOT:
    - Invent new mechanisms
    - Add any information not in the Ground Truth
    - Modify the summary yourself
    - Accept summaries prematurely

    Required output format of your response, must use one of this format:
    - If any unresolved, solvable issue exists:  
    REVISE:  
        1) <Problem description>  
        2) <Specific correction instruction>  
        … (list all issues)
    - If **everything is correct**:
        ACCEPT
    - If remaining issues are persistent issue or inherently ambiguous: 
        ACCEPT, BUT AGREE TO DISAGREE: <Explain why this cannot be corrected>

    CRITICAL OUTPUT CONTRACT:
    Your response MUST begin immediately with ONE of the following exact tokens 
    (with no text, explanation, or header before it):

    REVISE:
    ACCEPT
    ACCEPT, BUT AGREE TO DISAGREE:

    Do NOT write anything before this token.
    Do NOT add headers such as "Evaluation Report".
    Do NOT include markdown formatting.
        
    **Moderator Summary**:
    {summary}

    **Ground Truth**:
    {rag}
    """

##############################################################################
#Respond only with JSON.
    print("\n📌 === LLM Prompt ===")
    print(f"\nPrompt Size: {len(prompt)}")
    print("\n📌====================")
    print(f"Full Prompt: {prompt}")
##############################################################################
    verdict = call_llm(prompt, api, config_list, llm_config)

    text = verdict.choices[0].message.content.strip()
    print("\n✔=== LLM Response ===")
    print(f"\nResponse Size: {len(text)}")
    print("\n✔====================")
    print(f"\nFull Response: {text}")
    return text
