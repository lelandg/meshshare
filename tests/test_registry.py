from datetime import datetime, timedelta, timezone

import pytest

from meshshare.config import MeshShareConfig
from meshshare.models import PeerRegistration
from meshshare.registry import PeerRegistry


@pytest.fixture()
def config(tmp_path):
    shared_dir = tmp_path / "shared"
    shared_dir.mkdir()
    return MeshShareConfig(
        node_name="alpha",
        node_address="https://alpha.mesh",
        shared_dir=shared_dir,
        api_token="secret-token",
        allow_cidrs=["100.64.0.0/10"],
        deny_cidrs=["100.64.2.0/24"],
        allow_peer_ids=["alpha", "nick-box"],
        deny_peer_ids=["blocked-box"],
        peer_ttl_seconds=120,
    )


def test_register_peer_tracks_last_seen_and_visibility(config):
    registry = PeerRegistry(config)
    now = datetime(2026, 4, 12, 16, 0, tzinfo=timezone.utc)

    peer = PeerRegistration(
        peer_id="nick-box",
        display_name="Nick server",
        base_url="https://nick.mesh",
        tags=["meshnet", "files"],
    )

    registry.register(peer, remote_ip="100.64.1.10", now=now)
    active = registry.list_active(now=now)

    assert len(active) == 1
    assert active[0].peer_id == "nick-box"
    assert active[0].remote_ip == "100.64.1.10"
    assert active[0].last_seen == now


def test_denied_peer_id_is_rejected_even_if_ip_matches_allowlist(config):
    registry = PeerRegistry(config)

    with pytest.raises(PermissionError, match="peer is denied"):
        registry.register(
            PeerRegistration(
                peer_id="blocked-box",
                display_name="Blocked",
                base_url="https://blocked.mesh",
            ),
            remote_ip="100.64.1.20",
        )


def test_denied_cidr_is_rejected(config):
    registry = PeerRegistry(config)

    with pytest.raises(PermissionError, match="IP address is denied"):
        registry.register(
            PeerRegistration(
                peer_id="nick-box",
                display_name="Nick server",
                base_url="https://nick.mesh",
            ),
            remote_ip="100.64.2.15",
        )


def test_allowlist_requires_matching_peer_or_ip(config):
    registry = PeerRegistry(config)

    with pytest.raises(PermissionError, match="peer is not in allow list"):
        registry.register(
            PeerRegistration(
                peer_id="unknown-box",
                display_name="Unknown",
                base_url="https://unknown.mesh",
            ),
            remote_ip="100.64.1.10",
        )

    with pytest.raises(PermissionError, match="IP address is not in allow list"):
        registry.register(
            PeerRegistration(
                peer_id="nick-box",
                display_name="Nick server",
                base_url="https://nick.mesh",
            ),
            remote_ip="192.168.1.50",
        )


def test_stale_peers_are_hidden_after_ttl(config):
    registry = PeerRegistry(config)
    now = datetime(2026, 4, 12, 16, 0, tzinfo=timezone.utc)
    registry.register(
        PeerRegistration(
            peer_id="nick-box",
            display_name="Nick server",
            base_url="https://nick.mesh",
        ),
        remote_ip="100.64.1.10",
        now=now,
    )

    active = registry.list_active(now=now + timedelta(seconds=121))

    assert active == []
