from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from app.settings import settings


def _json_default(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


def write_jsonl(record: dict) -> None:
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / "audit.jsonl"

    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, default=_json_default) + "\n")