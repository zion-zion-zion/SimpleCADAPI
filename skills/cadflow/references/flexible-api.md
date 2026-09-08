# Flexible API (CadFlow 0.2.0)

Static cloth, leather, membranes, draped panels, and garments. This is geometry
generation, not cloth simulation. Source: CadFlow 0.2.0 `cadflow.flexible`.

```python
from cadflow.flexible import (
    FlexibleMaterial,
    FlexiblePanel,
    FlexibleModel,
    RingSection,
    sectioned_panel,
)
```

Do not put a cloth panel through `cad.Model` / `cad.Solid`. Do not add gravity,
collision, time integration, velocity, or XPBD.

## Representations

- `FlexiblePanel`: a rectangular control-point surface `(rows, columns, 3)`.
- `RingSection` + `sectioned_panel`: sleeves, legs, tubes, torsos, rolled sheets.
- `FlexibleModel`: named panels concatenated into one `FlexibleMesh`.

`FlexibleMaterial.thickness > 0` builds a closed thin shell. Thickness `0`
builds an open surface.

## Material

```python
fabric = FlexibleMaterial(
    name="cotton",
    thickness=1.2,                 # >= 0
    color=(0.17, 0.34, 0.52),      # each channel in [0, 1]
    roughness=0.68,                # in [0, 1]
)
```

## Arbitrary panel

```python
panel = FlexiblePanel(
    name="draped_sheet",
    control_points=control_grid,   # finite (rows, columns, 3), at least 2x2
    sample_rows=48,
    sample_columns=64,
    periodic_columns=False,
    material=fabric,
)
mesh = panel.build()
```

`sample_rows` / `sample_columns` must be at least the control-grid size.
`periodic_columns=True` needs at least three control columns.

## Sectioned panel

```python
sleeve = sectioned_panel(
    "left_sleeve",
    [
        RingSection((0, 0, 0), (1, 0, 0), (0, 1, 0), 40, 28),
        RingSection((0, 0, 180), (1, 0, 0), (0, 1, 0), 32, 24,
                    wrinkle_amplitude=0.02, wrinkle_count=6),
    ],
    control_columns=20,
    sample_rows=40,
    sample_columns=64,
    material=fabric,
)
```

`RingSection(center, axis_u, axis_v, radius_u, radius_v, wrinkle_amplitude=0,
wrinkle_count=6, wrinkle_phase=0)`: axes must be non-zero and orthogonal;
radii positive; `wrinkle_amplitude` in `[0, 0.5)`. Wrinkle fields are static
shape inputs, not a solver.

Start around 16–24 control columns and 32–64 sampled columns. Raise samples
where folds are tight, then recheck the mesh.

## Compose, measure, export

```python
model = FlexibleModel("static-garment")
model.add_panel(sleeve)
mesh = model.build()

print(mesh.vertex_count, mesh.triangle_count, mesh.bounds, mesh.surface_area)
print(mesh.is_watertight, [panel.name for panel in mesh.panels])

mesh.write_obj("out/sleeve.obj")
mesh.write_stl("out/sleeve.stl")      # binary
mesh.write_json("out/sleeve.json")    # counts, bounds, panel ranges, material
```

JSON is a mesh manifest, not motion state. OBJ keeps panel groups.

## Mesh checks

```python
import numpy as np

assert np.all(np.isfinite(mesh.vertices))
assert np.allclose(np.linalg.norm(mesh.normals, axis=1), 1.0, atol=1e-5)
assert int(mesh.triangles.max()) < mesh.vertex_count
assert mesh.triangle_count > 0
if any(panel.material.thickness > 0 for panel in mesh.panels):
    assert mesh.is_watertight

points = mesh.vertices[mesh.triangles]
areas = 0.5 * np.linalg.norm(
    np.cross(points[:, 1] - points[:, 0], points[:, 2] - points[:, 0]),
    axis=1,
)
assert float(areas.min()) > 1e-9
```

If folds self-intersect, change section geometry or wrinkle amplitude. That is
still a static shape, not physical drape.
