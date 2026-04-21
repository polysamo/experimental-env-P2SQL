from __future__ import annotations

import re
from pathlib import Path

import httpx
from app.settings import settings


SYSTEM_PROMPT = """
You are an LLM-to-SQL component for a job-market application.
Generate exactly one PostgreSQL SQL statement and nothing else.
Use only tables and columns from the provided schema.
Do not invent tables.
Do not invent columns.
Do not use markdown fences.
Do not explain the query.
Do not add comments.
If the request cannot be answered using only the provided schema, return an empty string.
Output SQL only.
""".strip()


SQL_HEADS = {"SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"}


def load_schema_description() -> str:
    path = Path("data/schema_description.txt")
    return path.read_text(encoding="utf-8") if path.exists() else ""


def extrair_sql_valida(texto: str) -> str:
    texto = str(texto or "").strip()

    if not texto:
        return ""

    # 1) bloco ```sql ... ```
    bloco_sql = re.search(r"```sql\s*(.*?)```", texto, flags=re.IGNORECASE | re.DOTALL)
    if bloco_sql:
        texto = bloco_sql.group(1).strip()
    else:
        # 2) qualquer bloco ``` ... ```
        bloco_generico = re.search(r"```(.*?)```", texto, flags=re.DOTALL)
        if bloco_generico:
            texto = bloco_generico.group(1).strip()

    texto = texto.strip()

    # 3) tenta achar a primeira instrução SQL plausível
    match = re.search(
        r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE)\b.*",
        texto,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match:
        texto = match.group(0).strip()

    # 4) corta no primeiro ponto e vírgula, mantendo só uma query
    if ";" in texto:
        texto = texto.split(";", 1)[0].strip() + ";"

    # 5) normaliza espaços
    texto = re.sub(r"\s+", " ", texto).strip()

    # 6) valida início
    if not texto:
        return ""

    primeira = texto.split()[0].upper()
    if primeira not in SQL_HEADS:
        return ""

    return texto


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

    with httpx.Client(timeout=120.0) as client:
        resp = client.post(
            f"{settings.openai_base_url.rstrip('/')}/chat/completions",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]
    return extrair_sql_valida(content)