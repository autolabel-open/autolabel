from typing import Any

from pydantic import BaseModel, Field, model_validator


class Operation(BaseModel):
    name: str
    service: str
    command: list[str]
    blocking: bool
    is_attack: bool = False


class Scene(BaseModel):
    services: dict[str, Any]
    networks: dict[str, Any]
    steps: list[Operation] = Field(..., alias="x-steps")
    attack_conns: list[str] = Field(..., alias="x-attack-conns", default_factory=list)

    @model_validator(mode="after")
    def validate_services(cls, v):
        services = v.services.keys()
        for step in v.steps:
            if step.service not in services:
                raise ValueError(f"Service {step.service} not found in services")
        return v
