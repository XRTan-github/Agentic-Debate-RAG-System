import re
from Helper.general_tools import call_llm
from config.llm_config import expert_config_list,Domain_Agent_llm_config,api
# =======================================================================================
# Domain expert Agent
# =========================
def domain_agent(domain, question,evidence, memory, critic_memory, config_list=expert_config_list, llm_config=Domain_Agent_llm_config,api=api):
    memory_context  = f"Previous Round Domains agents' arguments: \n{memory}" if memory else ""
    critic_memory_context  = f"Critic Feedback:\n{critic_memory}" if critic_memory else ""

    prompt = f"""
    You are a domain expert in **{domain}** engaged in a scientific debate.

    Your role:
    - Answer the **user question**. Provide a factual, mechanism-based explanation grounded ONLY in your domain expertise in **{domain}**.
    - You may use limited creativity to propose mechanistic links, but you MUST stay strictly aligned with the **Domain-Specific Evidence** and established science.
    - Do NOT invent data, external results, or facts not supported by the **Domain-Specific Evidence**.
    - Clearly distinguish between:
        - Evidence-supported reasoning
        - Hypothesis / speculation (label it explicitly)
    - Defend your domain’s perspective with maximum rigor.
    - Argue from domain-first principles — be assertive
    - Critique, challenge, or contradict other domain experts when they:
        - Overreach outside their domain
        - Make incorrect mechanistic claims
        - Draw conclusions unsupported by evidence

    **User question**:
    **{question}**

    **Domain-Specific Evidence**:
    **{evidence}**

    {memory_context}

    {critic_memory_context}

    Now produce a structured expert explanation with:
    1. Evidence-grounded mechanisms
    2. Domain-correct causal reasoning
    3. Optional labeled hypotheses (clearly separated)
    4. No content outside your expertise
    """
##############################################################################
#Respond only with JSON.
    print("📌 === LLM Prompt ===") 
    print(f"Prompt Size: {len(prompt)}")
    print("📌====================")
    print(f"Full Prompt: {prompt}")
##############################################################################
    response = call_llm(prompt, api, config_list, llm_config)
    reply = response.choices[0].message.content.strip()
##############################################################################
    print("✔=== LLM Response ===")
    print(reply)
    print("✔====================")

    return reply


