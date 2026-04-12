from pathlib import Path

from fastapi.testclient import TestClient

from meshshare.app import create_app
from meshshare.config import MeshShareConfig


def build_config(tmp_path: Path) -> MeshShareConfig:
    shared_dir = tmp_path / "shared"
    shared_dir.mkdir()
    (shared_dir / "hello.txt").write_text("hi nick\n", encoding="utf-8")
    (shared_dir / "nested").mkdir()
    (shared_dir / "nested" / "info.txt").write_text("mesh\n", encoding="utf-8")
    return MeshShareConfig(
        node_name="alpha",
        node_address="https://alpha.mesh",
        shared_dir=shared_dir,
        api_token="secret-token",
        allow_cidrs=[],
        deny_cidrs=[],
        allow_peer_ids=[],
        deny_peer_ids=[],
        peer_ttl_seconds=120,
    )


def test_root_page_lists_node_and_files(tmp_path):
    app = create_app(build_config(tmp_path))
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "alpha" in response.text
    assert "hello.txt" in response.text
    assert "nested/info.txt" in response.text


def test_file_index_requires_token(tmp_path):
    app = create_app(build_config(tmp_path))
    client = TestClient(app)

    unauthorized = client.get("/api/files")
    authorized = client.get("/api/files", headers={"X-MeshShare-Token": "secret-token"})

    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
    assert authorized.json()["files"][0]["path"] == "hello.txt"


def test_download_serves_file_contents(tmp_path):
    app = create_app(build_config(tmp_path))
    client = TestClient(app)

    response = client.get(
        "/files/hello.txt",
        headers={"X-MeshShare-Token": "secret-token"},
    )

    assert response.status_code == 200
    assert response.text == "hi nick\n"


def test_register_and_list_peers(tmp_path):
    app = create_app(build_config(tmp_path))
    client = TestClient(app)

    register = client.post(
        "/api/peers/register",
        headers={"X-MeshShare-Token": "secret-token"},
        json={
            "peer_id": "nick-box",
            "display_name": "Nick server",
            "base_url": "https://nick.mesh",
            "tags": ["meshnet"],
        },
    )
    peers = client.get("/api/peers", headers={"X-MeshShare-Token": "secret-token"})

    assert register.status_code == 200
    assert register.json()["status"] == "registered"
    assert peers.status_code == 200
    assert peers.json()["peers"][0]["peer_id"] == "nick-box"


def test_download_blocks_path_traversal(tmp_path):
    app = create_app(build_config(tmp_path))
    client = TestClient(app)

    response = client.get(
        "/files/../pyproject.toml",
        headers={"X-MeshShare-Token": "secret-token"},
    )

    assert response.status_code == 404
