# Pitfalls (CadFlow 0.2.0)

## Sessions

Every `cad.Shape` stores the session that created it. `cut`, `union`,
`translate`, and `distance_to` raise if the arguments come from different
`cad.Model` objects. Build one part in one `with cad.Model() as model:` block,
or pass the same `Model` around. Copy out `volume`, `bbox`, and `topology`
before the `with` block ends; querying a `Shape` after `Model.close()` raises
`NativeError: native session is closed`.

## Shape versus Solid

`model.box(...)` returns `cad.Shape`. `cad.make_box_rsolid(...)` returns
`cad.Solid`. `make_part_rpart(..., body=...)` accepts a Solid only. Do not
pass a frontend Shape into replayable booleans, and do not place assembly
occurrences with `model.translate`.

## Indices

`fillet`, `chamfer`, and `shell` take zero-based `edges` / `faces` indices.
`shape.topology` is the current count. After a boolean or blend, query again;
old indices can point at a different edge or fall out of range.
`model.preflight("fillet", shape, radius, edges=(...))` catches some of this
before the kernel call.

## Units and parameters

The API does not convert units. Mixing millimetres and metres silently builds
the wrong size. Convert at the input boundary. Reject non-positive radii,
zero-thickness shells, and through-cuts whose tool never overlaps the body.

Cylinders used as through-tools should extend past both faces of the body.

## Booleans

A failed `cut`/`union` is usually a placement problem: the tool misses the
body, only kisses an edge, or the operands are invalid. Print both bboxes and
volumes before changing dimensions. Do not return an arbitrary compound child
to hide a failed merge when the request was one solid.

`union_rsolid` needs face-area contact or volume overlap. Edge-only contact
stays non-manifold and raises.

## Validation versus kernel errors

`Shape.validate()` checks finite numbers and solid count. It does not prove
manufacturability, interference, or STEP translator fidelity. Reopen exported
STEP with `import_step` and compare measurements.

`report.ok` is false only for `error` diagnostics. A multiple-solid
`warning` still has `ok: true`; decide from the request whether that is
acceptable.

## Private imports

User programs use `import cadflow as cad` and public domain modules
(`cadflow.inspect`, `cadflow.flexible`, `cadflow.assembly` facades). Do not
import `cadflow._engine`, OCP/CadQuery classes, `ShapeHandle`, or load the
native library directly.

## Assemblies

Ground one component before `solve_assembly_constraints_rassembly(...,
strict=True)`. Duplicate `part_id` / `component_id` values raise. Connector
IDs must exist on the referenced component. Couplings (`gear`, `belt`) expect
those axes to already have revolute or prismatic supports.

## Environment

CadFlow 0.2.0 on PyPI is two wheels. A matching interpreter on the wrong OS,
or the right OS on the wrong Python, yields `no matching distribution`. That
is a package-publish limit, not a skill bug.
