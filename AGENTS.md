# Repository Guidelines

This repository ships one CadFlow skill. The skill is the product. Do not
rebuild a CAD agent, FastAPI backend, Viewer, executor, or benchmark platform.

## Layout

- `skills/cadflow/` — installable skill. `SKILL.md` is the always-loaded
  entry; `references/` and `examples/` load on demand.
- `tests/` — distribution integrity plus example execution against CadFlow
  0.2.0 from PyPI. These tests are maintainer checks, not a user modeling
  pipeline.
- `README.md` / `README.zh-CN.md` — install the same skill into Codex, Pi, or
  Claude Code.

The skill directory is self-contained. After install, hosts must not need any
file outside `skills/cadflow/`.

## CadFlow version

Documented and tested against **CadFlow 0.2.0** on PyPI. Wheels exist for
CPython 3.12 / Linux x86_64 (`manylinux_2_31`) and CPython 3.13 / macOS 12
arm64. Do not copy older Harness Python or platform limits, and do not vendor
wheels.

## Commands

```bash
uv venv --python 3.13 .venv          # 3.12 on Linux x86_64
uv pip install --python .venv/bin/python cadflow==0.2.0 pytest pyyaml
.venv/bin/python -m pytest
.venv/bin/python skills/cadflow/examples/mounting_plate.py
.venv/bin/python skills/cadflow/examples/hinge_assembly.py
```

## Skill writing

Keep `SKILL.md` short: trigger, environment, one working pattern, and pointers.
Put API detail in `references/`. Use `import cadflow as cad`. State real API
constraints (session ownership, Solid vs Shape, index selection) without
inventing file names, entry functions, or review stages.

## License

MIT. See `LICENSE`. CadFlow itself is a separate PyPI package.
