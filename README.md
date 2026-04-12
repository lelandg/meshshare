# MeshShare

MeshShare is a lightweight Linux-hosted file sharing and peer discovery service.
It is designed to work on ordinary networks, but it becomes much safer when you
run it over a private overlay such as Meshnet/Tailscale and restrict access with
allow/deny rules plus a shared API token.

## MVP features

- Read-only file sharing from a configured directory
- Peer registration and active-peer listing
- Allow/deny rules for peer IDs and CIDR ranges
- Simple built-in HTML status page
- JSON APIs for files and peers
- Path traversal protection on downloads
- `Justfile` for setup, test, lint, and local serving

## Project status

This is the initial MVP. The current version keeps peer state in memory and is
meant to validate the workflow before adding persistence, stronger auth, richer
UI, and multi-instance sync.

## Quick start

```bash
git clone https://github.com/lelandg/meshshare.git
cd meshshare
just setup
cp config.example.yaml config.yaml
mkdir -p shared
just test
source .venv/bin/activate
uvicorn meshshare.app:create_app --factory --host 0.0.0.0 --port 8080
```

Then open `http://<host>:8080/`.

## Example config

```yaml
node_name: alpha
node_address: https://alpha.mesh
shared_dir: ./shared
api_token: change-me
allow_cidrs:
  - 100.64.0.0/10
deny_cidrs: []
allow_peer_ids:
  - alpha
  - nick-box
deny_peer_ids: []
peer_ttl_seconds: 120
```

## Security model for the MVP

1. Prefer binding the service to a private mesh/VPN interface.
2. Set a non-trivial `api_token`.
3. Restrict traffic with `allow_cidrs` and/or `allow_peer_ids`.
4. Use `deny_*` rules as emergency blocks.
5. Keep the shared directory read-only unless/until uploads are implemented.

## API summary

### `GET /`
Human-readable status page with node name and current file list.

### `GET /api/files`
Returns the current file index. Requires `X-MeshShare-Token` when `api_token` is set.

### `GET /files/{path}`
Downloads a shared file. Path traversal outside the shared directory is blocked.

### `POST /api/peers/register`
Registers or refreshes a peer.

Example body:

```json
{
  "peer_id": "nick-box",
  "display_name": "Nick server",
  "base_url": "https://nick.mesh",
  "tags": ["meshnet", "files"]
}
```

### `GET /api/peers`
Lists active peers that have not expired past the configured TTL.

## Next steps

- Persistent peer storage
- Signed peer registration instead of shared-token-only auth
- Better web UI with peer health and file browsing
- Instance-to-instance pull/push replication options
- Admin UI for managing allow/deny rules
- Optional Meshnet-specific helpers and interface auto-detection

## Development

```bash
just setup
just test
just lint
```
