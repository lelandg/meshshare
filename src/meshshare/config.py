from pathlib import Path

from pydantic import BaseModel, Field


class MeshShareConfig(BaseModel):
    node_name: str
    node_address: str
    shared_dir: Path
    api_token: str | None = None
    allow_cidrs: list[str] = Field(default_factory=list)
    deny_cidrs: list[str] = Field(default_factory=list)
    allow_peer_ids: list[str] = Field(default_factory=list)
    deny_peer_ids: list[str] = Field(default_factory=list)
    peer_ttl_seconds: int = 120
