
import re
from Helper.general_tools import call_llm
from config.llm_config import general_config_list,general_llm_config,api

    # ----------------------------
    # 1. General-purpose Task Analyzer
    # ----------------------------
def analyze_task_general(question,config_list=general_config_list, llm_config=general_llm_config,api=api):
    """
    Extract all key entities and their types, plus relations from a question.
    """
    prompt = f"""
    You are an expert system whose ONLY job is to extract:
    1. **common_context** — entities that apply to ALL aspects of the question
    2. **variants** — entities representing different scientific dimensions
    being evaluated, optimized, or contrasted within the same context.

    --------------------------------------------
    ### 1. CORE INTERPRETATION LOGIC
    --------------------------------------------

    A **variant** is ANY entity (property, mechanism, structure, process, condition, or composition)
    that represents a DISTINCT scientific aspect being analyzed, contrasted, or optimized.

    A **common_context** entity is:
    - a composition, property, mechanism, environment, or condition shared across ALL variants
    - a global context for the scientific question

    Explicit comparison words (“vs”, “than”, “better than”) are NOT required for variants.

    --------------------------------------------
    ### 2. ENTITY EXTRACTION RULES
    --------------------------------------------

    - Extract each scientific entity exactly as written.
    - MUST treat any phrase inside **double asterisks (“**...**”)** as a single entity.
    - Classify each entity into one type from:
    ["composition", "property", "structure", "mechanism", "process", "condition"]

    --------------------------------------------
    ### 3. VARIANT CLASSIFICATION RULES
    --------------------------------------------

    An entity belongs to **variants** if ANY of the following are true:

    1. It is a property, mechanism, condition, or process being modified, compared, or optimized
    for the same composition.

    2. The question expresses:
    - improvement
    - optimization
    - comparison
    - performance differences
    - multiple scientific dimensions of a system

    3. The entity represents a dimension whose variation could be debated
    by separate scientific agents.

    4. (CRITICAL) **Composition Comparison Rule**:
    If the question compares, contrasts, or evaluates multiple compositions:
    - All compositions being compared MUST be placed in **variants**
    - Any property or mechanism being compared MUST be placed in **common_context**

    --------------------------------------------
    ### 4. COMMON CONTEXT RULES
    --------------------------------------------

    Place an entity in **common_context** if:
    - it is shared across all variants
    - it applies globally to the entire question
    - it is the property or mechanism used to compare two compositions

    --------------------------------------------
    ### 5. OUTPUT FORMAT (STRICT JSON)
    --------------------------------------------
    
    Return **strict JSON only**, with no explanation:

    {{
    "common_context": [
        {{"name": "...", "type": "..." }}
    ],
    "variants": [
        {{
        "name": "...",
        "type": "..."
        }},
        {{
        "name": "...",
        "type": "..."
        }}
    ]
    }}
    --------------------------------------------
    ### Now analyze the question:

    Question: "{question}"

    """
##############################################################################
#Respond only with JSON.
    print("\n📌 === LLM Prompt ===")
    print(f"\nPrompt Size: {len(prompt)}")
    print("\n📌====================")
    print(f"\nFull Prompt: {prompt}")
##############################################################################
    response = call_llm(prompt, api, config_list, llm_config)

    reply = response.choices[0].message.content.strip()
    cleanedreply = re.sub(r"^```(?:json)?|```$", "", reply.strip(), flags=re.MULTILINE).strip()
    ##############################################################################
    print("\n=== LLM Response ===")
    print(cleanedreply)
    print("====================")

    return cleanedreply
