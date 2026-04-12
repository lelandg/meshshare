from __future__ import annotations

from datetime import timezone
from pathlib import Path
from typing import Annotated

import yaml
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse

from meshshare.config import MeshShareConfig
from meshshare.models import PeerRegistration
from meshshare.registry import PeerRegistry


class AppState:
    def __init__(self, config: MeshShareConfig):
        self.config = config
        self.registry = PeerRegistry(config)


def load_config(path: str | Path) -> MeshShareConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return MeshShareConfig(**raw)


HeaderToken = Annotated[str | None, Header(alias="X-MeshShare-Token")]


def create_app(config: MeshShareConfig | None = None) -> FastAPI:
    if config is None:
        config_path = Path("config.yaml")
        config = load_config(config_path)

    app = FastAPI(title="MeshShare", version="0.1.0")
    state = AppState(config)
    app.state.meshshare = state

    def require_token(token: HeaderToken = None) -> None:
        if state.config.api_token and token != state.config.api_token:
            raise HTTPException(status_code=401, detail="missing or invalid token")

    def build_file_index() -> list[dict[str, str | int]]:
        files = []
        for path in sorted(state.config.shared_dir.rglob("*")):
            if path.is_file():
                relative = path.relative_to(state.config.shared_dir).as_posix()
                files.append({"path": relative, "size": path.stat().st_size})
        return files

    def resolve_file(file_path: str) -> Path:
        requested = (state.config.shared_dir / file_path).resolve()
        base = state.config.shared_dir.resolve()
        if base == requested or base not in requested.parents:
            if requested != base:
                raise HTTPException(status_code=404, detail="file not found")
        if not requested.is_file():
            raise HTTPException(status_code=404, detail="file not found")
        return requested

    @app.get("/", response_class=HTMLResponse)
    def home() -> str:
        files = build_file_index()
        file_items = "".join(f"<li>{item['path']}</li>" for item in files) or "<li>No files</li>"
        return (
            f"<html><body><h1>MeshShare: {state.config.node_name}</h1>"
            f"<p>Address: {state.config.node_address}</p>"
            f"<h2>Shared files</h2><ul>{file_items}</ul></body></html>"
        )

    @app.get("/api/files")
    def list_files(_: None = Depends(require_token)):
        return {"node": state.config.node_name, "files": build_file_index()}

    @app.get("/files/{file_path:path}")
    def download_file(file_path: str, _: None = Depends(require_token)):
        return FileResponse(resolve_file(file_path))

    @app.post("/api/peers/register")
    def register_peer(
        peer: PeerRegistration,
        request: Request,
        _: None = Depends(require_token),
    ):
        remote_ip = request.client.host if request.client else "127.0.0.1"
        if remote_ip == "testclient":
            remote_ip = "127.0.0.1"
        try:
            record = state.registry.register(peer, remote_ip=remote_ip)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        return {"status": "registered", "peer": record.model_dump(mode="json")}

    @app.get("/api/peers")
    def list_peers(_: None = Depends(require_token)):
        peers = [peer.model_dump(mode="json") for peer in state.registry.list_active()]
        return {"generated_at": timezone.utc.tzname(None), "peers": peers}

    return app
