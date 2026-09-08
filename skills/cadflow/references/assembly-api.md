# Assembly API (CadFlow 0.2.0)

Model separately manufactured parts, occurrences, connectors, and joints.
Source: CadFlow 0.2.0 public `make_*` / `add_*` operations
(`make_part_rpart`, `make_assembly_rassembly`, and related names).

A frontend `cad.Shape` from `cad.Model` is not a valid Part body. Stay in the
replayable `cad.Solid` family for assembly parts, then place occurrences with
component placements.

## Solids

```python
plate = cad.make_box_rsolid(
    width=40.0,      # local X
    height=24.0,     # local Y
    depth=8.0,       # local Z
    bottom_face_center=(0.0, 0.0, 0.0),
)
pin = cad.make_cylinder_rsolid(
    radius=4.0,
    height=20.0,
    bottom_face_center=(0.0, 0.0, 0.0),
    axis=(0.0, 0.0, 1.0),
)
body = cad.union_rsolid(plate, boss)
cut = cad.cut_rsolid(body, tool, skip_non_intersecting=False)
```

`make_box_rsolid` sizes X/Y/Z from `bottom_face_center`. Union members must
meet in area or volume so the result stays one connected `cad.Solid`.

## Parts and connectors

```python
part = cad.make_part_rpart(part_id="base", body=plate, name="Base")
part = cad.add_connector_rpart(
    part=part,
    connector=cad.make_placement_connector_rconnector(
        connector_id="hinge_axis",
        placement=cad.make_placement_rplacement(origin=(0.0, 0.0, 8.0)),
        name="Hinge axis",
    ),
)
```

`make_part_rpart` requires exactly one `cad.Solid`. Use
`make_face_connector_rconnector(connector_id, face, name=None, flip=False)`
when the datum is a selected BREP face. Use a placement connector for an
explicit local frame. `make_placement_rplacement(origin, x_axis=(1,0,0),
y_axis=(0,1,0))` builds a right-handed frame.

## Structure

```python
assembly = cad.make_assembly_rassembly(assembly_id="hinge", name="Hinge")
assembly = cad.add_component_rassembly(
    assembly=assembly,
    item=base_part,
    component_id="base",
    placement=cad.identity_placement_rplacement(),
    name="Base",
)
assembly = cad.add_component_rassembly(
    assembly=assembly,
    item=arm_part,
    component_id="arm",
    placement=cad.make_placement_rplacement(origin=(0.0, 0.0, 8.0)),
    name="Arm",
)
```

`item` is a `cad.Part` or nested `cad.Assembly`. Reuse one Part object for
repeated occurrences. Component IDs are unique within the parent.

```python
assembly = cad.forward_connector_rassembly(
    assembly=assembly,
    connector_id="input_axis",
    source_component_id="input_shaft",
    source_connector_id="axis",
    name="Module input axis",
)
```

## Joints

```python
def ref(component_id: str, connector_id: str):
    return cad.make_connector_ref_rconnectorref(component_id, connector_id)

assembly = cad.ground_component_rassembly(assembly, "base")
assembly = cad.add_revolute_constraint_rassembly(
    assembly=assembly,
    constraint_id="hinge_revolute",
    connector_a=ref("base", "hinge_axis"),
    connector_b=ref("arm", "hinge_axis"),
    drive_angle_degrees=0.0,
    name="Hinge rotation",
)
```

Also available:

- `add_fixed_constraint_rassembly(..., connector_a, connector_b, name=None)`
- `add_prismatic_constraint_rassembly(..., drive_distance=None, distance_limit=None)`
- `add_gear_constraint_rassembly(..., pitch_radius_a, pitch_radius_b)`
- `add_belt_constraint_rassembly(..., pulley_radius_a, pulley_radius_b)`
- `add_rack_pinion_constraint_rassembly(..., rack_connector, pinion_connector, pitch_radius)`

Limits: `cad.make_scalar_limit_rscalarlimit(lower_value, upper_value)`.
Couplings relate existing joint axes; they do not build gear teeth.

## Solve, inspect, export

```python
assembly = cad.solve_assembly_constraints_rassembly(assembly, strict=True)
report = cad.inspect_assembly_constraints_rconstraintreport(assembly)
assert report.solved
assert not report.unsolved_component_ids
assert all(item.within_tolerance for item in report.residuals)

compound = cad.make_compound_from_assembly_rcompound(assembly)
cad.export_step(shapes=compound, filename="hinge.step")
```

Inspect residuals, not only `report.solved`. Ground one fixed component before
a strict solve. Export the projected compound (or individual solids) through
the public export functions; there is no required `build_model` return value.
