import re
from Helper.general_tools import call_llm
from config.llm_config import expert_config_list,general_llm_config,api


# ---------- LLM composition + conditions extractor ----------
def RAG_summary(topic_tags,rag_text,max_tokens, config_list=expert_config_list, llm_config=general_llm_config,api=api):
    prompt = f"""
You are an materials scientist specializing in summary scientific information.

Your task: Summarize the extracted scientific information into a concise, structured narrative optimized for downstream reasoning by agent-based systems.

You must prioritize information summary relevant to: [{topic_tags}]
-----------------------
### STRICT SUMMARY REQUIREMENTS
1. **Start the summary by stating the composition(s)** mentioned in the information.  
2. **Preserve *all mechanistic relationships***, relevant to the target topics.  
3. **Do not hallucinate or invent information.** Everything must trace directly to the provided text.  
4. **If multiple factors are connected (processing → structure → property → mechanism), preserve the chain.**  
5. **Group information logically** in this implicit order:
   - Composition → Processing → Mechanisms → Structure → Mechanisms → Property  
6. Focus on causal, mechanistic, and rate-controlling explanations.  
7. Keep the explanation compact, coherent, and domain-accurate.
-----------------------
### Extracted Scientific Information:
{rag_text}
-----------------------
### Output Requirements:
- You may output up to **{max_tokens} tokens** if needed.
- Produce **one continuous narrative paragraph** unless a short list improves clarity.
- Emphasize **mechanisms**, **causal relationships**, **oxide scale behavior**,  
  and **any information relevant to [{topic_tags}]**.
- Avoid bullet-explosions and avoid restating node IDs or metadata.

Begin your summary below.
"""
##############################################################################
#Respond only with JSON.
    print("\n📌 === LLM Prompt ===")
    print(f"\nPrompt Size: {len(prompt)}")
    print("\n📌====================")
    print(f"Full Prompt: {prompt}")
##############################################################################
    # response = call_llm(prompt,client,config_list,llm_config,retries=5)
    response = call_llm(prompt, api, config_list, llm_config)
    print(response)
    reply = response.choices[0].message.content.strip()
    print("\n✔=== LLM Response ===")
    print(reply)
    print("\n====================")


    
    return reply
