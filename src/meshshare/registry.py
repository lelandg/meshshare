from __future__ import annotations

from datetime import datetime, timezone
import ipaddress

from meshshare.config import MeshShareConfig
from meshshare.models import PeerRecord, PeerRegistration


class PeerRegistry:
    def __init__(self, config: MeshShareConfig):
        self.config = config
        self._peers: dict[str, PeerRecord] = {}

    def register(
        self,
        peer: PeerRegistration,
        remote_ip: str,
        now: datetime | None = None,
    ) -> PeerRecord:
        self._validate(peer.peer_id, remote_ip)
        now = now or datetime.now(timezone.utc)
        record = PeerRecord(**peer.model_dump(), remote_ip=remote_ip, last_seen=now)
        self._peers[peer.peer_id] = record
        return record

    def list_active(self, now: datetime | None = None) -> list[PeerRecord]:
        now = now or datetime.now(timezone.utc)
        active: list[PeerRecord] = []
        for record in self._peers.values():
            age = (now - record.last_seen).total_seconds()
            if age <= self.config.peer_ttl_seconds:
                active.append(record)
        return sorted(active, key=lambda item: item.peer_id)

    def _validate(self, peer_id: str, remote_ip: str) -> None:
        ip = ipaddress.ip_address(remote_ip)

        if peer_id in self.config.deny_peer_ids:
            raise PermissionError("peer is denied")
        if self.config.allow_peer_ids and peer_id not in self.config.allow_peer_ids:
            raise PermissionError("peer is not in allow list")

        if any(ip in ipaddress.ip_network(cidr) for cidr in self.config.deny_cidrs):
            raise PermissionError("IP address is denied")
        if self.config.allow_cidrs and not any(
            ip in ipaddress.ip_network(cidr) for cidr in self.config.allow_cidrs
        ):
            raise PermissionError("IP address is not in allow list")
