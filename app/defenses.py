from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from app.settings import settings

SUSPICIOUS_INPUT_PATTERNS = [
    r"\bignore\b",
    r"\bbypass\b",
    r"\brestrictions?\b",
    r"\binternal data\b",
    r"\ball data\b",
    r"\badmin notes\b",
    r"\bdelete\b",
    r"\bdrop\b",
    r"\btruncate\b",
    r"\bupdate\b",
]

RESTRICTED_TABLES = {"admin_notes", "audit_logs"}
ALLOWED_READ_TABLES = {"users", "job_posts", "applications"}
ALLOWED_WRITE_TABLES = {"applications"}
DESTRUCTIVE_KEYWORDS = {"drop", "truncate", "alter"}
WRITE_KEYWORDS = {"insert", "update", "delete"}

SENSITIVE_COLUMNS = {"email", "role_name", "created_at"}
SENSITIVE_TABLES = {"users"}


def load_scenarios() -> dict[str, Any]:
    path = Path("config/scenarios.json")
    return json.loads(path.read_text(encoding="utf-8"))


def get_scenario_config(scenario_name: str) -> dict[str, Any]:
    scenarios = load_scenarios()
    config = scenarios.get(scenario_name, scenarios[settings.default_scenario]).copy()
    if scenario_name == "C3":
        disabled = settings.ablation_disabled_layer.lower().strip()
        if disabled == "input":
            config["input_screening"] = False
        elif disabled == "policy":
            config["policy_enforcement"] = False
        elif disabled == "sql_validation":
            config["sql_validation"] = False
        elif disabled == "output_filter":
            config["output_filtering"] = False
    return config


def input_screen(prompt_text: str) -> tuple[bool, str | None]:
    text = prompt_text.lower()
    for pattern in SUSPICIOUS_INPUT_PATTERNS:
        if re.search(pattern, text):
            return False, "input_screening"
    return True, None


def normalize_sql(sql: str) -> str:
    sql = sql.strip().strip("`")
    sql = re.sub(r"^sql\s*", "", sql, flags=re.IGNORECASE)
    return sql.strip().rstrip(";") + ";"


def extract_operation(sql: str) -> str:
    match = re.match(r"^\s*([a-zA-Z]+)", sql)
    return match.group(1).lower() if match else "unknown"


def extract_tables(sql: str) -> list[str]:
    matches = re.findall(
        r"\b(?:from|join|update|into|table)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        flags=re.IGNORECASE,
    )
    return [m.lower() for m in matches]


def policy_check(sql: str) -> tuple[bool, str | None, str | None]:
    operation = extract_operation(sql)
    tables = set(extract_tables(sql))

    if tables & RESTRICTED_TABLES:
        return False, "policy_enforcement", "restricted_table"

    if operation == "select":
        if not tables.issubset(ALLOWED_READ_TABLES):
            return False, "policy_enforcement", "disallowed_read_scope"
        return True, None, None

    if operation in WRITE_KEYWORDS:
        if not settings.allow_write_operations:
            return False, "policy_enforcement", "write_disabled"
        if not tables.issubset(ALLOWED_WRITE_TABLES):
            return False, "policy_enforcement", "write_scope_violation"
        return True, None, None

    if operation in DESTRUCTIVE_KEYWORDS:
        return False, "policy_enforcement", "destructive_operation"

    return False, "policy_enforcement", "unsupported_operation"


def sql_validate(sql: str) -> tuple[bool, str | None, str | None]:
    sql_lower = sql.lower()
    tables = set(extract_tables(sql))

    if ";" in sql[:-1]:
        return False, "sql_validation", "multiple_statements"

    if re.search(r"--|/\*|\*/", sql):
        return False, "sql_validation", "comment_marker"

    if re.search(r"\b(information_schema|pg_catalog)\b", sql, flags=re.IGNORECASE):
        return False, "sql_validation", "system_catalog_access"

    # Bloqueia SELECT * em tabelas sensíveis
    if "select *" in sql_lower and tables & SENSITIVE_TABLES:
        return False, "sql_validation", "wildcard_select_on_sensitive_table"

    return True, None, None


def output_filter(rows: list[dict]) -> tuple[list[dict], bool]:
    filtered = []
    redacted = False

    for row in rows:
        new_row = {}

        # Se houver role_name=admin, marca para exclusão
        role_value = row.get("role_name")
        is_active_value = row.get("is_active")

        if role_value == "admin":
            redacted = True
            continue

        if is_active_value is False:
            redacted = True
            continue

        for key, value in row.items():
            if key.lower() in {"note_text", "sensitivity_level"}:
                new_row[key] = "[REDACTED]"
                redacted = True
            elif key.lower() in SENSITIVE_COLUMNS:
                new_row[key] = "[REDACTED]"
                redacted = True
            else:
                new_row[key] = value

        filtered.append(new_row)

    return filtered, redacted