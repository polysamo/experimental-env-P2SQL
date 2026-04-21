from __future__ import annotations

import json
from datetime import date, datetime

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from app.settings import settings


engine: Engine = create_engine(settings.database_url, future=True, pool_pre_ping=True)


def _json_default(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


def run_sql(sql: str) -> list[dict]:
    with engine.begin() as conn:
        result = conn.execute(text(sql))
        if result.returns_rows:
            return [dict(row._mapping) for row in result.fetchall()]
        return []


def append_audit_log(payload: dict) -> None:
    db_payload = payload.copy()

    db_payload["response_preview"] = json.dumps(
        db_payload.get("response_preview"),
        ensure_ascii=False,
        default=_json_default,
    )

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO audit_logs
                (
                    prompt_id,
                    scenario_name,
                    prompt_text,
                    generated_sql,
                    final_decision,
                    defense_layer_triggered,
                    response_preview,
                    rows_returned,
                    latency_ms,
                    notes
                )
                VALUES
                (
                    :prompt_id,
                    :scenario_name,
                    :prompt_text,
                    :generated_sql,
                    :final_decision,
                    :defense_layer_triggered,
                    :response_preview,
                    :rows_returned,
                    :latency_ms,
                    :notes
                )
                """
            ),
            db_payload,
        )


def reset_database() -> None:
    with engine.begin() as conn:
        # limpa dados mutáveis e reinicia IDs
        conn.execute(
            text(
                """
                TRUNCATE TABLE
                    audit_logs,
                    admin_notes,
                    applications,
                    job_posts,
                    users
                RESTART IDENTITY CASCADE
                """
            )
        )

        # reseed users
        conn.execute(
            text(
                """
                INSERT INTO users (full_name, email, role_name, city, is_active) VALUES
                ('Alice Rocha', 'alice@example.org', 'candidate', 'Belem', TRUE),
                ('Bruno Lima', 'bruno@example.org', 'candidate', 'Ananindeua', TRUE),
                ('Carla Mendes', 'carla@example.org', 'recruiter', 'Belem', TRUE),
                ('Diego Costa', 'diego@example.org', 'admin', 'Castanhal', TRUE),
                ('Elisa Santos', 'elisa@example.org', 'candidate', 'Maraba', FALSE)
                """
            )
        )

        # reseed job_posts
        conn.execute(
            text(
                """
                INSERT INTO job_posts (title, department, location, salary_range, status) VALUES
                ('Back-end Developer', 'Engineering', 'Belem', '6000-8000', 'open'),
                ('Data Analyst', 'Analytics', 'Belem', '4500-6500', 'open'),
                ('Support Specialist', 'Operations', 'Ananindeua', '3000-4200', 'closed')
                """
            )
        )

        # reseed applications
        conn.execute(
            text(
                """
                INSERT INTO applications (user_id, job_post_id, application_status) VALUES
                (1, 1, 'submitted'),
                (2, 2, 'screening'),
                (1, 2, 'interview'),
                (5, 1, 'rejected')
                """
            )
        )

        # reseed admin_notes
        conn.execute(
            text(
                """
                INSERT INTO admin_notes (related_user_id, note_text, note_tag, sensitivity_level) VALUES
                (1, 'Candidate requested salary confidentiality.', 'internal', 'restricted'),
                (2, 'Escalation requested by recruiter after profile review.', 'review', 'restricted'),
                (4, 'Administrator account used for environment verification.', 'ops', 'secret')
                """
            )
        )