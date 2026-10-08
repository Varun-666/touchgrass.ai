from typing import Literal
from pydantic import BaseModel, Field, field_validator

Mode = Literal["nature", "explore", "garden"]
Energy = Literal["low", "medium", "high"]
Setting = Literal["park", "garden", "neighborhood", "trail", "balcony", "backyard", "anywhere"]


class MissionRequest(BaseModel):
    mode: Mode = "nature"
    duration: int = Field(default=30, ge=10, le=180)
    energy: Energy = "low"
    setting: Setting = "park"
    interests: list[str] = Field(default_factory=list, max_length=8)
    goal: str = Field(default="I want to spend some time outside", max_length=300)

    @field_validator("interests")
    @classmethod
    def clean_interests(cls, values: list[str]) -> list[str]:
        cleaned = []
        for value in values:
            value = value.strip().lower()
            if value and value not in cleaned:
                cleaned.append(value[:40])
        return cleaned


class Mission(BaseModel):
    title: str
    reason: str
    duration_minutes: int
    steps: list[str]
    look_for: list[str]
    phone_rule: str
    safety: str
    closing_line: str
    model: str
    local: bool = True
