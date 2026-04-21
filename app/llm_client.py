from __future__ import annotations

import httpx
from pathlib import Path
from app.settings import settings


SYSTEM_PROMPT = """
You are an LLM-to-SQL component for a job-market application.
Generate exactly one PostgreSQL SQL statement and nothing else.
Use only tables and columns from the provided schema.
Do not use markdown fences.
""".strip()


def load_schema_description() -> str:
    path = Path("data/schema_description.txt")
    return path.read_text(encoding="utf-8") if path.exists() else ""


def generate_sql(prompt_text: str) -> str:
    schema_text = load_schema_description()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\nSchema:\n" + schema_text},
        {"role": "user", "content": prompt_text},
    ]
    payload = {
        "model": settings.openai_model,
        "messages": messages,
        "temperature": 0,
    }
    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(f"{settings.openai_base_url.rstrip('/')}/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return str(content).strip()
