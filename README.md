# CadFlow Skill

A self-contained [Agent Skill](https://agentskills.io/specification) for
modeling CAD geometry with [CadFlow](https://pypi.org/project/cadflow/0.2.0/).
Install the same directory into Codex, Pi, or Claude Code. The host agent
prepares a CadFlow environment, then writes and runs ordinary Python.

CadFlow is the modeling interface. This repository is not a CAD agent, backend,
Viewer, or execution service.

English · [简体中文](README.zh-CN.md)

## What you get

```text
skills/cadflow/
├── SKILL.md                 # trigger, environment, minimal pattern
├── agents/openai.yaml       # optional Codex / ChatGPT display metadata
├── references/              # API, pitfalls, inspect/export
└── examples/                # part and assembly programs
```

The skill targets **CadFlow 0.2.0** on PyPI. Published wheels:

- CPython 3.12 on Linux x86_64 (`manylinux_2_31`)
- CPython 3.13 on macOS 12+ arm64

PyPI metadata lists a wider Python range; only those two wheels exist for
0.2.0. Installer errors on other platforms are package-publish limits.

## Install the skill

The canonical skill is `skills/cadflow`. This checkout also links that directory
into `.agents/skills/cadflow`, `.pi/skills/cadflow`, and `.claude/skills/cadflow`
so Codex, Pi, and Claude Code load it as a project skill without copying the
body. For other working directories, symlink the same folder:

### Pi

```bash
mkdir -p ~/.pi/agent/skills
ln -sfn /path/to/CadFlow-Harness/skills/cadflow ~/.pi/agent/skills/cadflow
```

Project install: `mkdir -p .pi/skills && ln -sfn ../skills/cadflow .pi/skills/cadflow`.
Pi also loads `--skill /path/to/skills/cadflow`. Invoke with `/skill:cadflow`.

### Codex

```bash
mkdir -p ~/.agents/skills
ln -sfn /path/to/CadFlow-Harness/skills/cadflow ~/.agents/skills/cadflow
```

Project install: `mkdir -p .agents/skills && ln -sfn ../skills/cadflow .agents/skills/cadflow`.
Codex scans `.agents/skills` from the working directory up to the repo root,
then `~/.agents/skills`. Mention `$cadflow` or type `/skills`.

### Claude Code

```bash
mkdir -p ~/.claude/skills
ln -sfn /path/to/CadFlow-Harness/skills/cadflow ~/.claude/skills/cadflow
```

Project install: `mkdir -p .claude/skills && ln -sfn ../skills/cadflow .claude/skills/cadflow`.
Invoke with `/cadflow`. Claude Code must be logged in (`claude` / `/login`) before
it will load project skills.

After install the skill must not read files outside that directory.

## Use it

Ask the agent to model a part or assembly. It should:

1. Create an isolated venv and `uv pip install cadflow==0.2.0` (or `pip`).
2. Write a Python program that uses `import cadflow as cad`.
3. Run that program with the venv interpreter.
4. Validate measurements and reopen exported STEP.

Example environment check:

```bash
uv venv --python 3.13 .venv     # 3.12 on Linux x86_64
uv pip install --python .venv/bin/python cadflow==0.2.0
.venv/bin/python - <<'PY'
import cadflow as cad
with cad.Model() as model:
    print(cad.__version__, model.box(2, 3, 4).volume)
PY
```

You do not need this repository's old backend, Viewer, model API keys, or a
self-hosted executor. Host model credentials belong to Codex / Pi / Claude
Code, not to CadFlow.

## Maintainer checks

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python cadflow==0.2.0 pytest pyyaml
.venv/bin/python -m pytest
.venv/bin/python skills/cadflow/examples/mounting_plate.py
.venv/bin/python skills/cadflow/examples/hinge_assembly.py
```

These tests confirm the skill archive and that the bundled examples still run
against the published wheel. They are not a user-facing modeling pipeline.

## License

MIT. See [LICENSE](LICENSE). CadFlow is a separate PyPI package with its own
license.
