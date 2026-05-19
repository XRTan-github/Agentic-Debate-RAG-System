import re
from Helper.general_tools import call_llm
from config.llm_config import general_config_list,general_llm_config,api
# ---------- LLM composition + conditions extractor ----------
def extract_composition(name, config_list=general_config_list, llm_config=general_llm_config,api=api):
    prompt = f"""
You are an expert in alloy composition parsing.

Input context: {name}.

Task:
Given the text above, extract one or more alloy compositions referenced in the text.
You must convert any shorthand composition name (e.g., "NiCoCrAlFe alloy", "equiatomic NiCoCr") into a full explicit numeric composition.

GENERAL EXTRACTION RULES:
1. If the text contains a composition string (e.g., "Ni20Co20Cr20Fe20Al20"), parsing it exactly.
2. If the text uses a shorthand name (e.g., "NiCoCrAlFe alloy"), assume **equiatomic** unless stated otherwise.
3. Output `"composition_string"` exactly as in input context

4. In `"composition_elements"`:
    - Always output the **full composition with explicit numeric values** for every element.
    - Numbers must be floats rounded to 5 decimal place.
    - Element symbols must be standard chemical symbols (e.g., Ni, Co, Cr).
    - If an element is the **balance element**, calculate its value as `100 - sum(all other numeric amounts)` and fill in `"amount"`.
    - If no number is given or it is a trace amount(e.g., "0.001 ppm"), store `"text"` as in the paper and `"amount"` as 0.
    - If a range is given (e.g., 20–25at% Al), store the range as `"text"` and `"amount"` as the midpoint.

STRICT RESPONSE RULES:
- Respond ONLY with valid JSON.
- Do NOT include text, commentary, markdown code fences, or explanations before or after the JSON.
- The JSON must be a **single JSON array** (a list `[...]` of objects), where each object represents one sample entry.
- Do NOT return multiple top-level objects or extra text.
- Ensure the JSON is valid and parsable by Python json.loads().

Return JSON with this format:
    {{
    "composition_string": "composition string as in input",
    "composition_elements": [
        {{
            "element": "Ni",
            "amount": float or 0 if trace/balance,
            "text": "original string from text"
        }},
        {{
            "element": "Co",
            "amount": float or 0 if trace/balance,
            "text": "original string from text"
        }}
    ]
    }}
"""
##############################################################################
#Respond only with JSON.
    print("📌 === LLM Prompt ===")
    print(f"Prompt Size: {len(prompt)}")
    print("📌====================")
    print(f"Full Prompt: {prompt}")
##############################################################################
    response = call_llm(prompt, api, config_list, llm_config)

    print(response)
    reply = response.choices[0].message.content.strip()
    cleanedreply = re.sub(r"^```(?:json)?|```$", "", reply.strip(), flags=re.MULTILINE).strip()
##############################################################################
    print("✔=== LLM Response ===")
    print(cleanedreply)
    print("====================")

    return cleanedreply
###############################################################################################################################
