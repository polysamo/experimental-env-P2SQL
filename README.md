# Experimental Environment for Direct Prompt Attacks on LLM-to-SQL

This scaffold provides a reproducible experimental environment aligned with your paper design:

- **FastAPI** application exposing a single `/query` endpoint
- **PostgreSQL** database with synthetic data
- **LLM-to-SQL module** using an OpenAI-compatible API
- **Scenario-based defenses** for `C0`, `C1`, `C2`, and `C3`
- **Structured logs** for prompt, generated SQL, decision, and response

## Scenarios

- `C0`: no defense
- `C1`: simple defense (input screening + operation allowlist)
- `C2`: defense in depth (input screening + policy + SQL validation + output filtering + auditing)
- `C3`: ablation (same as C2, but disable one selected layer)

## Project layout

```text
experimental_env/
  app/
    main.py
    settings.py
    db.py
    llm_client.py
    defenses.py
    schemas.py
    audit.py
  db/init/
    01_schema.sql
    02_seed.sql
  config/
    scenarios.json
  data/
    schema_description.txt
  .env.example
  docker-compose.yml
  requirements.txt
```

## Quick start

1. Copy `.env.example` to `.env` and adjust values.
2. Start services:

```bash
docker compose up --build
```

3. Open API docs at:

```text
http://localhost:8000/docs
```

## Example request

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_id": "B001_DIR1",
    "prompt_text": "List open job posts.",
    "scenario_name": "C0"
  }'
```

## Important notes

- The LLM endpoint is **not bundled**. Point `OPENAI_BASE_URL` to your local LM Studio, Ollama-compatible proxy, or other OpenAI-compatible endpoint.
- The SQL execution path is intentionally conservative. By default, only a single statement is allowed.
- This is a **research scaffold**, not a production security system.

## How this maps to the paper

- **Threat model**: attacker acts only through natural-language input.
- **Environment**: one base application with layered defenses added by scenario.
- **Metrics/logging**: each request records prompt, generated SQL, decision, defense layer, latency, and response summary.
