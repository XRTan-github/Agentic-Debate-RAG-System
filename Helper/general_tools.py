import json
import time
import random
from openai import OpenAI
# ==== Robust call_llm that builds client from apilist[0] ====
def call_llm(prompt, api, config_list, llm_config):

    api_key = api
    client = OpenAI(api_key=api_key, base_url=config_list[0]['base_url'])
    model = config_list[0]['model']
    temp = llm_config.get('temperature', 0)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temp
    )

    return response

# ======================================
# Helper Function: Normalize Composition after LLM extracted composition
# ======================================
def normalize_composition(comp_elements):
    """
    Generate a canonical composition key based on elements and their numeric amounts,
    ignoring order and text formatting.
    """
    if not comp_elements:
        return "unknown"

    # Build dictionary {element: amount}
    comp_dict = {}
    for e in comp_elements:
        try:
            el = e.get("element")
            amt = float(e.get("amount", 0))
            if el:
                comp_dict[el] = amt
        except (ValueError, TypeError):
            continue

    # Sort by element name to ensure consistent order
    normalized = "-".join([f"{el}{comp_dict[el]}" for el in sorted(comp_dict.keys())])
    return normalized
###############################################################################################################################
# ======================================
# Helper Function: conver composition key to vector so that can calculate composition similarity
# ======================================
ELEMENTS = ['Al','Co','Cr','Ni','Fe','Si','Y','Hf','Nb','Mn','C','Mo','B','Zr','W',
'Ti','Ta','V','S','C','Cu','N','Ce','P','Re','La','Sn','Mg','Sc','O','Dy','Pt','Y2O3','Th','Ru','H',
'Na','Ca','Cr2O3','SiO2','Al2O3','TiO2','La2O3','Eu2O3','CeO2','Sm2O3','Gd2O3','MgO','ZrO2','Ta2O5',
'TiO2','Yb2O3','Dy2O3','Lu2O3','Er2O3','Ho2O3','Tb2O3','Gd','Pd','Sm','Yb','Nd']
def compkey_to_vector(comp_key, elements=ELEMENTS):
    """
    comp_key: string like "Al24.0-Co16.0-Cr22.0-Fe8.0-Ni30.0"
    returns: list of floats in ELEMENTS order
    """
    vec = []
    comp_dict = {}
    for part in comp_key.split('-'):
        elem = ''.join([c for c in part if c.isalpha()])
        amt = ''.join([c for c in part if c.isdigit() or c=='.'])
        if elem and amt:
            comp_dict[elem] = float(amt)
    for e in elements:
        vec.append(comp_dict.get(e, 0.0))
    return vec

