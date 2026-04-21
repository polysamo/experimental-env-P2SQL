from __future__ import annotations

import time
from fastapi import FastAPI, HTTPException
from app.audit import write_jsonl
from app.db import append_audit_log, run_sql, reset_database
from app.defenses import (
    get_scenario_config,
    input_screen,
    normalize_sql,
    output_filter,
    policy_check,
    sql_validate,
)
from app.llm_client import generate_sql
from app.schemas import QueryRequest, QueryResponse

app = FastAPI(title="LLM-to-SQL Experimental Environment", version="0.1.0")


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}

@app.post("/admin/reset-db")
def reset_db_endpoint() -> dict:
    reset_database()
    return {"status": "ok", "message": "Database reset and reseeded successfully"}

@app.post("/query", response_model=QueryResponse)
def query_endpoint(req: QueryRequest) -> QueryResponse:
    start = time.perf_counter()
    scenario = get_scenario_config(req.scenario_name)
    rows = []
    defense_layer_triggered = None
    final_decision = "allowed"
    generated_sql = None
    response_preview = None
    notes = None

    try:
        if scenario.get("input_screening"):
            allowed, layer = input_screen(req.prompt_text)
            if not allowed:
                defense_layer_triggered = layer
                final_decision = "blocked"
                notes = "blocked at input screening"
                raise HTTPException(status_code=403, detail="Request blocked by input screening")

        generated_sql = normalize_sql(generate_sql(req.prompt_text))

        sql_head = generated_sql.strip().split()[0].upper() if generated_sql and generated_sql.strip() else ""

        if not generated_sql or not str(generated_sql).strip():
            final_decision = "invalid_generation"
            notes = "empty_or_invalid_sql_generation"
            raise HTTPException(status_code=400, detail="LLM did not return valid SQL")

        if sql_head not in {"SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"}:
            final_decision = "invalid_generation"
            notes = "non_sql_llm_output"
            raise HTTPException(status_code=400, detail="LLM output is not valid SQL")

        if scenario.get("policy_enforcement"):
            allowed, layer, reason = policy_check(generated_sql)
            if not allowed:
                defense_layer_triggered = layer
                final_decision = "blocked"
                notes = reason
                raise HTTPException(status_code=403, detail=f"Request blocked by policy: {reason}")

        if scenario.get("sql_validation"):
            allowed, layer, reason = sql_validate(generated_sql)
            if not allowed:
                defense_layer_triggered = layer
                final_decision = "blocked"
                notes = reason
                raise HTTPException(status_code=403, detail=f"Request blocked by SQL validation: {reason}")

        try:
            rows = run_sql(generated_sql)
        except Exception as e:
            final_decision = "db_error"
            notes = f"database execution error: {str(e)}"
            response_preview = None
            raise HTTPException(status_code=400, detail="Database execution error")
        
        if scenario.get("output_filtering"):
            rows, redacted = output_filter(rows)
            if redacted:
                defense_layer_triggered = defense_layer_triggered or "output_filtering"
                notes = (notes + "; redaction applied") if notes else "redaction applied"
        response_preview = rows[:10]

        return QueryResponse(
            prompt_id=req.prompt_id,
            scenario_name=req.scenario_name,
            generated_sql=generated_sql,
            final_decision=final_decision,
            defense_layer_triggered=defense_layer_triggered,
            response_preview=response_preview,
            latency_ms=int((time.perf_counter() - start) * 1000),
            notes=notes,
        )
    finally:
        latency_ms = int((time.perf_counter() - start) * 1000)
        preview_for_log = response_preview[:5] if isinstance(response_preview, list) else response_preview
        rows_returned = len(response_preview) if isinstance(response_preview, list) else 0

        record = {
            "prompt_id": req.prompt_id,
            "scenario_name": req.scenario_name,
            "prompt_text": req.prompt_text,
            "generated_sql": generated_sql,
            "final_decision": final_decision,
            "defense_layer_triggered": defense_layer_triggered,
            "response_preview": preview_for_log,
            "rows_returned": rows_returned,
            "latency_ms": latency_ms,
            "notes": notes,
        }

        write_jsonl(record)
        append_audit_log(record)