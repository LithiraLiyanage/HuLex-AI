
import csv
import json
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "hc3_raw.jsonl"
OUTPUT_FILE = DATA_DIR / "dataset.csv"

random.seed(42)

pairs = []
seen = set()

with INPUT_FILE.open("r", encoding="utf-8") as file:
    for group_id, line in enumerate(file):
        item = json.loads(line)

        human_answers = item.get("human_answers", [])
        ai_answers = item.get("chatgpt_answers", [])

        human = next(
            (x.strip() for x in human_answers
             if isinstance(x, str) and len(x.split()) >= 30),
            None
        )

        ai = next(
            (x.strip() for x in ai_answers
             if isinstance(x, str) and len(x.split()) >= 30),
            None
        )

        if human is None or ai is None:
            continue

        human = " ".join(human.split())
        ai = " ".join(ai.split())

        if human == ai:
            continue

        if human.lower() in seen or ai.lower() in seen:
            continue

        seen.add(human.lower())
        seen.add(ai.lower())

        pairs.append({
            "group_id": group_id,
            "source": item.get("source", "unknown"),
            "human": human,
            "ai": ai
        })

random.shuffle(pairs)

selected = pairs[:5000]

with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["text", "label", "group_id", "source"])

    for pair in selected:
        writer.writerow([
            pair["human"], 0,
            pair["group_id"], pair["source"]
        ])
        writer.writerow([
            pair["ai"], 1,
            pair["group_id"], pair["source"]
        ])

print("Dataset preparation complete!")
print("Human samples:", len(selected))
print("AI samples:", len(selected))
print("Total samples:", len(selected) * 2)
print("Saved to:", OUTPUT_FILE)
