---
name: cadflow
description: CadFlow Python CAD modeling from PyPI. Use when writing or editing a CadFlow program for a mechanical part, assembly, static cloth, membrane, or garment, preparing a compatible CadFlow environment, exporting STEP, STL, or OBJ, or inspecting CadFlow solids and flexible meshes. CadFlow's native Python API is the modeling interface.
license: MIT
compatibility: Requires a published CadFlow 0.2.0 wheel (Python 3.12 on Linux x86_64 manylinux_2_31, or Python 3.13 on macOS 12+ arm64), uv or pip, and network access to PyPI.
metadata:
  cadflow_version: "0.2.0"
  pypi: "https://pypi.org/project/cadflow/0.2.0/"
---

# CadFlow

Write an ordinary Python program. CadFlow builds the geometry. The host's file
and terminal tools are enough; there is no separate CAD agent, backend, viewer,
or execution service.

Selected release: **CadFlow 0.2.0** on PyPI (wheels uploaded 2026-09-08).
API notes below match that release's public frontend, not a source checkout.

## Prepare the environment

Create an isolated environment in the user's working directory. Do not modify
system Python or an unrelated project environment.

```bash
# macOS 12+ arm64
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python cadflow==0.2.0

# Linux x86_64, glibc 2.31+
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python cadflow==0.2.0
```

`uv venv` does not install pip. Use `uv pip install --python .venv/bin/python ...`,
not `.venv/bin/pip`. Stdlib venv still works:
`python3.13 -m venv .venv && .venv/bin/pip install cadflow==0.2.0`.
Honor the host's network and execution permissions. If PyPI has no wheel for
the current interpreter or platform, stop and report the installer error.
Do not fall back to CadFlow source builds or local wheels to hide a publish gap.

Verify:

```bash
.venv/bin/python - <<'PY'
import cadflow as cad
with cad.Model() as model:
    box = model.box(2, 3, 4)
    print(cad.__version__, box.volume)
PY
```

Expect version `0.2.0` and a box volume of 24 (floating-point error is fine).
Read [references/environment.md](references/environment.md)
for the tested matrix, provenance, and installer failures.

## Model

Use `import cadflow as cad`. Keep one consistent numeric unit, normally millimetres.

```python
from pathlib import Path
import cadflow as cad

out = Path("mounting_plate.step")
with cad.Model() as model:
    plate = model.box(80, 50, 8)
    bore = model.translate(model.cylinder(radius=6, height=12), 20, 25, -2)
    part = model.cut(plate, bore)
    report = part.validate()
    if not report.ok:
        raise RuntimeError(report.to_dict())
    print(part.describe())
    part.export_step(str(out))
```

- One rigid manufactured solid: `cad.Model` / `cad.Shape`.
- Separately manufactured parts, placements, connectors, or joints: the
  replayable Part/Assembly API.
- Static cloth, leather, membranes, draped panels, garments: `cadflow.flexible`.
  That path is a triangle shell, not a BREP solid.
- Keep every `Shape` inside the `Model` that created it.
- After each boolean or finishing feature, read `describe()`, `validate()`,
  volume, bbox, and topology. Repair from those facts.
- Export STEP/STL only after the measured result matches the request.
- Reopen STEP with `model.import_step(...)` before treating the file as done.

Organize the program however the task needs. There is no required filename,
entry function, project layout, tool-call order, or review stage.

## Load on demand

| When | Read |
| --- | --- |
| Constructors, sketches, booleans, fillets | [references/part-api.md](references/part-api.md) |
| Parts, placements, connectors, constraints | [references/assembly-api.md](references/assembly-api.md) |
| Cloth, membranes, garments | [references/flexible-api.md](references/flexible-api.md) |
| Measure, validate, import, export | [references/inspect-export.md](references/inspect-export.md) |
| Session, Solid vs Shape, indices, units | [references/pitfalls.md](references/pitfalls.md) |
| Runnable programs | [examples/mounting_plate.py](examples/mounting_plate.py), [examples/hinge_assembly.py](examples/hinge_assembly.py), [examples/sleeve_panel.py](examples/sleeve_panel.py) |

Copy patterns from the examples; do not treat them as a required scaffold.
