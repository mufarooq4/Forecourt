import os
import sqlite3                               
from dotenv import load_dotenv
from groq import Groq

def run_query(sql):
    conn = sqlite3.connect("file:../data/forecourt.db?mode=ro", uri=True)
    try:
        rows = conn.execute(sql).fetchall()
        result = str(rows[:20])
        if len(rows) > 20:
            result += (f"\n(Only the first 20 of {len(rows)} rows are shown. "
                       f"Use ORDER BY and LIMIT so the rows that matter come first.)")
        return result
    except Exception as e:
        return f"ERROR: {e}"         
    finally:
        conn.close()

def ask(question):
    load_dotenv()
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    schema = open("../data/schema.sql", encoding="utf-8").read()

    response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": f"You write SQLite queries for this database {schema}. Reply with only the SQL, no explanation.The data runs up to 2026-11-08. Treat 2026-11-08 as today."},
        # {"role": "user", "content": "What was the total revenue on 2026-11-08?"},
        {"role": "user", "content": f"{question}"},
    ],  
    )

    text = response.choices[0].message.content
    sql = text.replace("```sql", "").replace("```", "").strip()

    conn = sqlite3.connect("file:../data/forecourt.db?mode=ro", uri=True)

    rows = conn.execute(sql).fetchall()
    # print(sql)
    # print(rows)

    return sql, rows


if __name__ == "__main__":
    print(run_query("SELECT COUNT(*) FROM stations"))
    print(run_query("SELECT COUNT(*) FROM petrol_pumps"))
    sql, rows = ask("What was the total revenue on 2026-11-08?")
    print(sql)
    print(rows)

    sql, rows = ask("How many stations are in Karachi?")
    print(sql)
    print(rows)

    sql, rows = ask("Which station sold the most diesel in the last 7 days?")
    print(sql)
    print(rows)


