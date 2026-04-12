from datetime import datetime

from pydantic import BaseModel, Field


class PeerRegistration(BaseModel):
    peer_id: str
    display_name: str
    base_url: str
    tags: list[str] = Field(default_factory=list)


class PeerRecord(PeerRegistration):
    remote_ip: str
    last_seen: datetime
