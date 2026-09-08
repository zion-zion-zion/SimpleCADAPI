# CadFlow 0.2.0 environment

Install CadFlow from PyPI into an isolated environment. The skill does not
ship wheels, a Python launcher, or a run manager.

## Selected release

| Field | Value |
| --- | --- |
| Package | `cadflow` |
| Version | `0.2.0` |
| PyPI | https://pypi.org/project/cadflow/0.2.0/ |
| Requires-Python metadata | `>=3.10,<3.14` |
| Published wheels | `cadflow-0.2.0-cp312-cp312-manylinux_2_31_x86_64.whl` |
|  | `cadflow-0.2.0-cp313-cp313-macosx_12_0_arm64.whl` |
| Upload time | 2026-09-08 |
| Runtime deps pulled by the wheel | `numpy`, `rich`, `cadquery-ocp==7.9.3.1`, `jsonschema`, `rfc8785`, `typing-extensions`, `py-slvs==1.0.6`, `ocp-gordon` |

PyPI metadata lists Python 3.10–3.13 classifiers, but **0.2.0 only publishes
two wheels**. A 3.10/3.11 interpreter, Linux aarch64, macOS x86_64, or Windows
host will fail at install time. Report that failure; do not hide it with a
CadFlow source checkout.

API text in this skill was checked against CadFlow 0.2.0 public modules
(`cadflow.frontend.Model`/`Shape`, `cadflow._engine.geometry.operations` public
`make_*`/`add_*` names) and the CadFlow 0.2.0 README / modern-frontend guide.

## Tested combinations

| Host | Interpreter | Installer | Package | Result |
| --- | --- | --- | --- | --- |
| macOS 12+ arm64 | CPython 3.13 | `uv pip install --python .venv/bin/python cadflow==0.2.0` | PyPI wheel | tested by this repository |
| Linux x86_64, glibc 2.31+ | CPython 3.12 | `uv pip install --python .venv/bin/python cadflow==0.2.0` | PyPI wheel | CI target; local Linux not required on the authoring machine |

Prefer `uv`. `python -m pip` in the same isolated venv is the fallback.

## Install

Work in the user's project directory, or a new directory the user named.

```bash
uv venv --python 3.13 .venv          # 3.12 on Linux x86_64
uv pip install --python .venv/bin/python cadflow==0.2.0
.venv/bin/python -c "import cadflow as cad; print(cad.__version__)"
```

`uv venv` does not include pip. `uv pip install --python .venv/bin/python ...`
targets that interpreter. Stdlib venv still has pip:

```bash
python3.13 -m venv .venv
.venv/bin/pip install cadflow==0.2.0
```

Rules:

- Do not install into the system interpreter.
- Do not add CadFlow to an unrelated project's dependencies unless the user
  asked to.
- Do not use repository vendor wheels or `pip install ./CadFlow`.
- If the host blocks network access, stop and say CadFlow cannot be installed.

## Smoke check

```python
import cadflow as cad

with cad.Model() as model:
    box = model.box(2, 3, 4)
    assert cad.__version__ == "0.2.0"
    assert abs(box.volume - 24.0) < 1e-9
```

A native-library error at import or `model.box` is an environment problem.
Paste the exact command and traceback.

## Optional extras

CadFlow's wheel already includes the geometry kernel. PNG rendering helpers
under `cadflow.inspect` may ask for `matplotlib`, `vtk`, or `pillow`. Install
those only when the user asked for rendered views. STEP/STL export does not
need them.
