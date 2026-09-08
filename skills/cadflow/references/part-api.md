# Part API (CadFlow 0.2.0)

Use `import cadflow as cad`. Arguments are unitless floats; pick one unit for
the whole program, normally millimetres.

Source: CadFlow 0.2.0 `cadflow.frontend.Model` / `cadflow.frontend.Shape`.

## Session

```python
with cad.Model() as model:
    plate = model.box(80, 50, 8)
```

`Model` owns the native session. Every returned `Shape` belongs to that
session. Close the model (the `with` block does this) when the program is
done. Do not mix shapes from two models.

## Constructors

```python
box = model.box(width, depth, height)
cyl = model.cylinder(radius, height)
sph = model.sphere(radius)
cone = model.cone(radius1, radius2, height)

wire = model.polyline([(0, 0, 0), (20, 0, 0), (20, 10, 0), (0, 10, 0)], closed=True)
circle = model.circle_profile(radius, center=(0, 0, 0), normal=(0, 0, 1))
arc = model.arc(start, middle, end)
spline = model.interpolate(points, periodic=False, tolerance=1e-6)
helix = model.helix(pitch, height, radius, center=(0, 0, 0), direction=(0, 0, 1))
face = model.face(wire)
```

`box(width, depth, height)` maps to X, Y, Z extents with the first corner at
the origin. Cylinders and spheres sit on the session default axis.

## Features, booleans, transforms

```python
solid = model.extrude(face, x=0, y=0, z=10)
turned = model.revolve(face, degrees=360, axis=(0, 0, 1), origin=(0, 0, 0))
lofted = model.loft((profile_a, profile_b), solid=True, ruled=False)
swept = model.sweep(face, path, solid=True, frenet=False)
rounded = model.fillet(solid, radius=1.0, edges=(0, 1))
beveled = model.chamfer(solid, distance=0.5, edges=(0, 1))
hollow = model.shell(solid, thickness=1.0, faces=(0,), tolerance=1e-3)

cut_part = model.cut(body, tool)
joined = model.union(left, right)
common = model.intersect(left, right)

placed = model.translate(shape, x, y, z)
rotated = model.rotate(shape, degrees=90, axis=(0, 0, 1), origin=(0, 0, 0))
mirrored = model.mirror(shape, normal=(1, 0, 0), origin=(0, 0, 0))
scaled = model.scale(shape, factor=2.0, center=(0, 0, 0))
```

Query `shape.topology` before passing `edges` or `faces`. Those indices are
zero-based and can change after any topology-changing operation.

`model.faces(shape)` returns face handles. A planar face can be exported with
`face.export_dxf(path, tolerance=0.01)`.

## Sketch

```python
with model.workplane(origin=(10, 0, 5), normal=(0, 1, 0)) as plane:
    sketch = plane.sketch("mounting_profile")
    sketch = (sketch.add_point("a", 0, 0)
                    .add_point("b", 20, 0)
                    .add_point("c", 20, 10)
                    .add_point("d", 0, 10))
    sketch = (sketch.add_line("ab", "a", "b")
                    .add_line("bc", "b", "c")
                    .add_line("cd", "c", "d")
                    .add_line("da", "d", "a"))
    sketch = sketch.constrain_fix("a")
    solve = sketch.inspect(strict=False)
    face = sketch.to_native_face(model, strict=False)
```

Workplanes transform point arguments; they do not mutate existing shapes.
Promote a sketch to a face or wire before extrude, revolve, or a profile cut.

## Agent feedback

```python
print(model.capabilities())
pre = model.preflight("fillet", solid, 1.0, edges=(0, 1))
outcome = model.apply("cut", body, tool)
print(part.describe())
print(part.validate().to_dict())
```

`describe()`, `validate()`, `capabilities()`, `preflight()`, and `apply()`
return JSON-safe reports. `validate()` is an inexpensive check (finite
measurements, solid count). A `warning` about multiple solids is not a kernel
crash; decide whether the request wanted one solid.

## Replayable constructors

When the result must round-trip through model JSON, use `GraphSession`,
`@cad.model`, `cad.capture_result()`, and `cad.make_*_r*` / `cad.cut_rsolid` /
`cad.union_rsolid`. That family returns `cad.Solid`, not `cad.Shape`. See
[assembly-api.md](assembly-api.md) before wrapping a Solid as a Part.

Ordinary part scripts can stay on `cad.Model`.
