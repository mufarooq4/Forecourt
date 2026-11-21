import os
import json
from dotenv import load_dotenv
from text_to_sql import run_query              # your crash-proof tool from step 1
from groq import Groq, RateLimitError



def call_ai(messages, **extra):
    for attempt in range(3):
        try:
            return client.chat.completions.create(model="openai/gpt-oss-120b",
                                                  messages=messages, tools=tools, **extra)
        except RateLimitError:
            print("  (rate limit, waiting 30 s...)")
            time.sleep(30)
    raise RuntimeError("Still rate-limited after 3 tries.")

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
schema = open("../data/schema.sql", encoding="utf-8").read()

tools = [{
    "type": "function",
    "function": {
        "name": "run_query",
        "description": "Run one read-only SQLite query on the Forecourt database. "
                       "Returns up to 20 rows, or an error message.",
        "parameters": {
            "type": "object",
            "properties": {"sql": {"type": "string", "description": "A single SQLite SELECT query"}},
            "required": ["sql"],
        },
    },
}]

SYSTEM = (f"You answer questions about a petrol station database by running SQL "
          f"with the run_query tool.{schema}"
            "The data runs up to 2026-11-08; treat that as today."
            "Only state numbers and dates that came from your query results. If you need a number, query it."
            "Do calculations inside SQL with SUM, GROUP BY, ORDER BY and LIMIT, so each result is a small summary."
            "Never fetch raw rows to add them up yourself.\n"
            "For stock losses, leaks or theft, use the tank_reconciliation view and look across the whole period, not one day."
            "If a result looks impossible, such as every tank losing thousands of litres, suspect your query and check it.")


def run_agent(question, max_steps=8):
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]

    for step in range(max_steps):
        response = client.chat.completions.create(model="openai/gpt-oss-120b", messages=messages, tools=tools)
        msg = response.choices[0].message

        if not msg.tool_calls:              # no notes: this is the final answer
            return msg.content

        # Add the AI's notes to the transcript (it may send more than one)
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [{"id": c.id, "type": "function",
                            "function": {"name": c.function.name, "arguments": c.function.arguments}}
                           for c in msg.tool_calls],
        })

        # Run each note's SQL and add each result
        for c in msg.tool_calls:
            sql = json.loads(c.function.arguments)["sql"]
            result = run_query(sql)
            print(f"  step {step + 1}: {sql}")
            print(f"           -> {result[:120]}")
            messages.append({"role": "tool", "tool_call_id": c.id, "content": result})

    # return "Stopped: too many steps without a final answer."
    # Out of steps: ask for the best answer using what it has already found
    messages.append({"role": "user", "content": "You have run out of query steps. "
                     "Give your best answer now, using only the results you already have."})
    response = client.chat.completions.create(model="openai/gpt-oss-120b", messages=messages,
                                              tools=tools, tool_choice="none")
    return response.choices[0].message.content


if __name__ == "__main__":
    for q in ["How many stations are in Karachi?",
              "Which tank looks like it might have a leak? Investigate."]:
        print("Q:", q)
        print("A:", run_agent(q))
        print()