import re
from Helper.general_tools import call_llm
from config.llm_config import expert_config_list,Experiment_Agent_llm_config,api
# =======================================================================================
# 3. Experimental suggestion Agent
# =========================

def experiment_suggestion_agent(theory, config_list=expert_config_list, llm_config=Experiment_Agent_llm_config,api=api):
    prompt = f"""
    Given the proposed theory:

    **{theory}**

    Your task:
    - Suggest simple, practical experiments that can test the theory.
    - Each experiment must:
        - Specify what to measure
        - Specify key parameter(s) to vary
        - Describe expected results if the theory is correct
        - Describe expected results if the theory is incorrect
        - Keep suggestions minimal and focused. Avoid long lists.
"""
##############################################################################
#Respond only with JSON.
    print("\n📌 === LLM Prompt ===")
    print(f"\nPrompt Size: {len(prompt)}")
    print("\n📌====================")
    print(f"\nFull Prompt: {prompt}")
##############################################################################
    t = call_llm(prompt, config_list, llm_config)
    text = t.choices[0].message.content.strip()
    print("\n✔=== LLM Response ===")
    print(f"\nResponse Size: {len(text)}")
    print("\n✔====================")
    print(f"\nFull Response: {text}")
    return text