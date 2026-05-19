import json, os, datetime
############################################################################################################
HISTORY_DIR = "log"
os.makedirs(HISTORY_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(HISTORY_DIR, "question_history.json")
############################################################################################################
###Load & Save History
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
##Check if question already exists
def check_existing_answer(question):
    history = load_history()
    if question in history:
        checkpoint_path = history[question]["checkpoint_file"]
        if os.path.exists(checkpoint_path):
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                return json.load(f),checkpoint_path
    return None,None
############################################################################################################
###Save a checkpoint for a question
def save_checkpoint_for_question(question, checkpoint_data):
    history = load_history()
    # assign unique file
    idx = len(history) + 1
    fname = f"checkpoint_{idx:03d}.json"
    fname = os.path.join(HISTORY_DIR, fname)
    # save checkpoint data
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(checkpoint_data, f, indent=2)
    # update history
    history[question] = {
        "checkpoint_file": fname,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_history(history)
    return fname

##Update checkpoint incrementally (after each composition)
def update_checkpoint(question, checkpoint_data):
    history = load_history()
    if question not in history:
        return save_checkpoint_for_question(question, checkpoint_data)

    fname = history[question]["checkpoint_file"]

    with open(fname, "w", encoding="utf-8") as f:
        json.dump(checkpoint_data, f, indent=2)

    return fname




