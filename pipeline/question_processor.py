import json
import random
from LLM_agents.task_analyzer import analyze_task_general
from LLM_agents.composition_extractor import extract_composition
from Helper.general_tools import normalize_composition
from Helper.checkpoint_manager import check_existing_answer, update_checkpoint

def process_question(question):#
    reply = analyze_task_general(question)
    task_output = json.loads(reply)

    checkpoint = {
        "question": question,
        "task_output": task_output,
        "processed": {}
    }
    # Extract composition for all composition entries
    all_entries = (
        task_output.get("common_context", []) +
        task_output.get("variants", [])
    )

    for entry in all_entries:
        if entry.get("type") == "composition":
            name = entry["name"]

            text_str = extract_composition(name)
            tem = json.loads(text_str)
            comp_elems = tem[0]["composition_elements"]
            comp_key = normalize_composition(comp_elems)

            entry["composition_key"] = comp_key
            checkpoint["processed"][name] = comp_key

    update_checkpoint(question, checkpoint)

    return checkpoint