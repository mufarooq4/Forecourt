import json
import time
from text_to_sql import ask

items = [json.loads(line) for line in open("../data/eval.jsonl", encoding="utf-8")]

for item in items:
    print(item["id"], item["question"])
    print("   expected:", item["expected"])
    try:
        sql, rows = ask(item["question"])
        print("   got:     ", rows)
    except Exception as e:
        print("   ERROR:   ", e)
    time.sleep(10)