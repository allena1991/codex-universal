# AGENTS.md

## Cursor Cloud specific instructions

### What this repo is

`codex-universal` is a **Docker base image** repository — not a traditional application. There is no `package.json`, `Cargo.toml`, or other root-level dependency manifest. Development means building and running the Docker image defined in `Dockerfile`.

### Required tooling

- **Docker** must be installed and the daemon running (`sudo docker info` should succeed).
- In Cloud Agent VMs, Docker uses the `fuse-overlayfs` storage driver and `iptables-legacy`. The daemon may need to be started manually: `sudo dockerd > /tmp/dockerd.log 2>&1 &` (wait a few seconds before using Docker).
- Use `sudo docker` unless the current user is in the `docker` group.

### Build and run

| Task | Command |
|------|---------|
| Pull pre-built image | `sudo docker pull ghcr.io/openai/codex-universal:latest` |
| Build locally | `sudo docker build -t codex-universal:local /workspace` |
| Run interactively | See `README.md` for `docker run` with `CODEX_ENV_*` vars and workspace mount |
| Run a one-off command | Use `--entrypoint bash` to avoid the default entrypoint wrapping your command in `bash --login` |

Example non-interactive verification:

```sh
sudo docker run --rm --entrypoint bash \
  -e CODEX_ENV_PYTHON_VERSION=3.12 \
  -e CODEX_ENV_NODE_VERSION=20 \
  -v "$(pwd):/workspace/$(basename "$(pwd)")" \
  -w "/workspace/$(basename "$(pwd)")" \
  ghcr.io/openai/codex-universal:latest \
  -lc '/opt/codex/setup_universal.sh && python3 --version && node --version'
```

### Lint / test / verify

- No standalone lint or unit-test suite at the repo root.
- **Build-time verification**: `verify.sh` runs automatically during `docker build` and exercises `setup_universal.sh` across the full language version matrix.
- **Runtime verification**: run language commands inside the container after `setup_universal.sh` (see `verify.sh` for the full checklist).

### Build time expectations

A full local `docker build` installs many language runtimes and runs `verify.sh`; expect **30+ minutes**. For quick iteration, pull `ghcr.io/openai/codex-universal:latest` and test changes to `setup_universal.sh` / `entrypoint.sh` by mounting them or rebuilding only after Dockerfile edits.

### Environment variables

Optional `CODEX_ENV_*` variables select language versions at container start. See the table in `README.md` for supported values. No API keys or `.env` files are required for local development.
