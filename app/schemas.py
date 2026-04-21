from typing import Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    prompt_id: str = Field(..., description="Prompt identifier")
    prompt_text: str = Field(..., description="Natural-language input")
    scenario_name: str = Field(default="C0", description="Experimental scenario")
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    prompt_id: str
    scenario_name: str
    generated_sql: str | None
    final_decision: str
    defense_layer_triggered: str | None
    response_preview: Any
    latency_ms: int
    notes: str | None = None
