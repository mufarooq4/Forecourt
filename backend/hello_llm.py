import os
import sqlite3                               
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
schema = open("../data/schema.sql", encoding="utf-8").read()

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": f"You write SQLite queries for this database {schema}. Reply with only the SQL, no explanation."},
        {"role": "user", "content": "What was the total revenue on 2026-11-08?"},
    ],
)

text = response.choices[0].message.content
sql = text.replace("```sql", "").replace("```", "").strip()

conn = sqlite3.connect("file:../data/forecourt.db?mode=ro", uri=True)

rows = conn.execute(sql).fetchall()
print(sql)
print(rows)