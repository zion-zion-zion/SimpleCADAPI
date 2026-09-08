"""CadFlow 0.2.0 hinge: two parts, revolute joint, STEP reopen."""

from __future__ import annotations

from pathlib import Path

import cadflow as cad


def _axis_connector(connector_id: str, origin: tuple[float, float, float], name: str):
    return cad.make_placement_connector_rconnector(
        connector_id=connector_id,
        placement=cad.make_placement_rplacement(origin=origin),
        name=name,
    )


def build_hinge_assembly(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    step_path = output_dir / "hinge.step"

    base_body = cad.make_box_rsolid(
        width=40.0,
        height=24.0,
        depth=8.0,
        bottom_face_center=(0.0, 0.0, 0.0),
    )
    base = cad.make_part_rpart(part_id="base", body=base_body, name="Base")
    base = cad.add_connector_rpart(
        part=base,
        connector=_axis_connector("hinge_axis", (0.0, 0.0, 8.0), "Base hinge axis"),
    )

    arm_body = cad.make_box_rsolid(
        width=8.0,
        height=24.0,
        depth=40.0,
        bottom_face_center=(0.0, 0.0, 0.0),
    )
    arm = cad.make_part_rpart(part_id="arm", body=arm_body, name="Arm")
    arm = cad.add_connector_rpart(
        part=arm,
        connector=_axis_connector("hinge_axis", (0.0, 0.0, 0.0), "Arm hinge axis"),
    )

    assembly = cad.make_assembly_rassembly(assembly_id="hinge", name="Hinge")
    assembly = cad.add_component_rassembly(
        assembly=assembly,
        item=base,
        component_id="base",
        placement=cad.identity_placement_rplacement(),
        name="Base",
    )
    assembly = cad.add_component_rassembly(
        assembly=assembly,
        item=arm,
        component_id="arm",
        placement=cad.identity_placement_rplacement(),
        name="Arm",
    )
    assembly = cad.ground_component_rassembly(assembly, "base")
    assembly = cad.add_revolute_constraint_rassembly(
        assembly=assembly,
        constraint_id="hinge_revolute",
        connector_a=cad.make_connector_ref_rconnectorref("base", "hinge_axis"),
        connector_b=cad.make_connector_ref_rconnectorref("arm", "hinge_axis"),
        drive_angle_degrees=0.0,
        name="Hinge rotation",
    )
    assembly = cad.solve_assembly_constraints_rassembly(assembly, strict=True)
    report = cad.inspect_assembly_constraints_rconstraintreport(assembly)
    if not report.solved or report.unsolved_component_ids:
        raise RuntimeError(report.to_dict())
    if not all(item.within_tolerance for item in report.residuals):
        raise RuntimeError(report.to_dict())

    compound = cad.make_compound_from_assembly_rcompound(assembly)
    cad.export_step(shapes=compound, filename=str(step_path))

    with cad.Model() as model:
        imported = model.import_step(str(step_path))
        solids = imported.topology.get("solids")
        imported_volume = imported.volume
        if solids != 2:
            raise RuntimeError(f"expected two solids in STEP, got {imported.topology}")
        if imported_volume <= 0.0:
            raise RuntimeError("expected positive imported volume")

    return {
        "assembly_id": assembly.assembly_id,
        "components": list(assembly.component_ids()),
        "constraints": list(assembly.constraint_ids()),
        "solved": report.solved,
        "step": str(step_path),
        "imported_solids": solids,
        "imported_volume": imported_volume,
    }


def main() -> None:
    metrics = build_hinge_assembly(Path("out") / "hinge_assembly")
    print(metrics)


if __name__ == "__main__":
    main()
