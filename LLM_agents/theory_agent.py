import re
from Helper.general_tools import call_llm
from config.llm_config import expert_config_list,Theory_Agent_llm_config,api
# =======================================================================================
# Theory Agent
# =========================
def theory_agent(summary, config_list=expert_config_list, llm_config=Theory_Agent_llm_config,api=api):

    prompt = f"""
    You are a mechanistic materials scientist specializing in theory generation.

    Given the **accepted synthesis**:
    **{summary}**

    Your task:
    - Propose a brief, elegant, mechanistically sound theory.
    - The theory must be grounded STRICTLY in the **accepted synthesis**.
    - Creativity is allowed, but no external facts or new data may be introduced.
    - Keep it concise and focused on the core mechanism.
    """
##############################################################################
#Respond only with JSON.
    print("\n📌 === LLM Prompt ===")
    print(f"\nPrompt Size: {len(prompt)}")
    print("\n📌====================")
    print(f"\nFull Prompt: {prompt}")
##############################################################################
    t = call_llm(prompt, api, config_list, llm_config)
    text = t.choices[0].message.content.strip()
    print("\n✔=== LLM Response ===")
    print(f"\nResponse Size: {len(text)}")
    print("\n✔====================")
    print(f"\nFull Response: {text}")
    return text