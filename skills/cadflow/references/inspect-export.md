# Inspect and export (CadFlow 0.2.0)

Measurement and exchange are CadFlow API calls. They are not a required
workflow, review bot, or extra service.

## Shape queries

On a `cad.Shape` from `cad.Model`:

| Member | Meaning |
| --- | --- |
| `kind` | Shape class reported by the session |
| `volume`, `area`, `length` | Scalar measurements |
| `center_of_mass` | `(x, y, z)` |
| `bbox` | `(xmin, ymin, zmin, xmax, ymax, zmax)` |
| `topology` | Counts such as `solids`, `faces`, `edges` |
| `distance_to(other)` | Same-session distance |
| `describe(detail="summary")` | JSON-safe dict; `detail="mesh"` adds tessellation |
| `validate()` | Inexpensive finite-measurement / solid-count report |
| `mesh(deflection=0.1)` | Triangle buffer |

Compare bbox extents (`xmax - xmin`), not only the origin. A valid solid with
the wrong size is a failed deliverable.

```python
report = part.validate().to_dict()
assert report["ok"]
assert part.topology["solids"] == 1
assert part.volume > 0.0
```

`validate()` does not replace a kernel boolean error. If `cut`/`union` raises,
inspect overlap and bounds of the inputs first.

## Export and import

```python
part.export_step("part.step")
part.export_stl("part.stl", binary=True)
part.export_preview_glb("part.glb")
face.export_dxf("profile.dxf", tolerance=0.01)

with cad.Model() as model:
    imported = model.import_step("part.step")
    print(imported.volume, imported.topology)
```

`Model.import_step`, `import_brep`, and `import_stl` reopen files produced by
this package. After export, reopen the STEP and compare volume, bbox, and
solid count with the in-memory shape. File existence is not enough.

Replayable solids and assembly compounds use:

```python
cad.export_step(shapes=solid_or_compound, filename="out.step")
```

Create parent directories before writing.

## Assembly reports

```python
report = cad.inspect_assembly_constraints_rconstraintreport(assembly)
print(report.to_dict())
```

`ConstraintResidual` fields: `constraint_id`, `translation_error`,
`angular_error_degrees`, `within_tolerance`.

## STEP inspection (optional)

```python
from cadflow.inspect import brep

summary = brep.inspect_step_rsummary(path="part.step")
inspection = brep.inspect_step_rbrepinspection(path="part.step")
```

Use this when the input is an existing STEP file or when comparing two files.
Rendering helpers may need extra Python packages; skip them unless the user
asked for images.

## DXF

`Shape.export_dxf` writes closed outer and inner machining loops of a planar
face in millimetres. It is not a hidden-line view of the whole solid. Select
the face with `model.faces(part)` first.
