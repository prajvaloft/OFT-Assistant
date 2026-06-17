import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "data", "knowledge.json")


def load_db():
    if not os.path.exists(DB_FILE):
        return {}

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_db(db):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)


def get_answer(question):
    db = load_db()

    entry = db.get(question.lower())
    if not entry:
        return None

    if isinstance(entry, dict):
        answer = entry.get("answer")
        if answer and "no result found" not in answer:
            return answer
        return None
    if isinstance(entry,str):
        if "No results found" in entry:
            return None
        return entry

    return None


def get_entry(question):
    db = load_db()
    return db.get(question.lower())


def store_answer(question, answer):
    if not answer:
        return

    answer_str = str(answer)

    if "No results found" in answer_str:
        return

    db = load_db()

    db[question.lower()] = {
        "answer": answer,
        "updated": datetime.now().strftime("%Y-%m-%d")
    }

    save_db(db)