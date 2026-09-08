"""CadFlow 0.2.0 mounting plate: box, through-bore, STEP/STL, reopen."""

from __future__ import annotations

from pathlib import Path

import cadflow as cad


def build_mounting_plate(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    step_path = output_dir / "mounting_plate.step"
    stl_path = output_dir / "mounting_plate.stl"

    with cad.Model() as model:
        plate = model.box(80.0, 50.0, 8.0)
        bore = model.translate(model.cylinder(radius=6.0, height=12.0), 40.0, 25.0, -2.0)
        part = model.cut(plate, bore)
        report = part.validate()
        if not report.ok:
            raise RuntimeError(report.to_dict())
        if part.topology.get("solids") != 1:
            raise RuntimeError(f"expected one solid, got {part.topology}")
        if part.volume <= 0.0:
            raise RuntimeError("expected positive volume")

        part.export_step(str(step_path))
        part.export_stl(str(stl_path), binary=True)

        imported = model.import_step(str(step_path))
        volume_delta = abs(imported.volume - part.volume)
        if volume_delta > 1e-3:
            raise RuntimeError(
                f"reimported STEP volume {imported.volume} != {part.volume}"
            )

        metrics = {
            "kind": part.kind,
            "volume": part.volume,
            "bbox": list(part.bbox),
            "topology": dict(part.topology),
            "step": str(step_path),
            "stl": str(stl_path),
            "imported_volume": imported.volume,
            "imported_solids": imported.topology.get("solids"),
        }
    return metrics


def main() -> None:
    metrics = build_mounting_plate(Path("out") / "mounting_plate")
    print(metrics)


if __name__ == "__main__":
    main()
