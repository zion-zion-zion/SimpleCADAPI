"""CadFlow 0.2.0 static sleeve: sectioned thin shell, OBJ/STL, mesh checks."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from cadflow.flexible import (
    FlexibleMaterial,
    FlexibleModel,
    RingSection,
    sectioned_panel,
)


def build_sleeve_panel(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    obj_path = output_dir / "sleeve.obj"
    stl_path = output_dir / "sleeve.stl"
    json_path = output_dir / "sleeve.json"

    fabric = FlexibleMaterial(name="cotton", thickness=1.2)
    sleeve = sectioned_panel(
        "left_sleeve",
        [
            RingSection((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), 40.0, 28.0),
            RingSection(
                (0.0, 0.0, 180.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
                32.0,
                24.0,
                wrinkle_amplitude=0.02,
                wrinkle_count=6,
            ),
        ],
        control_columns=16,
        sample_rows=24,
        sample_columns=48,
        material=fabric,
    )
    model = FlexibleModel("static-sleeve")
    model.add_panel(sleeve)
    mesh = model.build()

    if not np.all(np.isfinite(mesh.vertices)):
        raise RuntimeError("mesh vertices are not finite")
    if int(mesh.triangles.max()) >= mesh.vertex_count:
        raise RuntimeError("triangle index out of range")
    if not mesh.is_watertight:
        raise RuntimeError("positive-thickness sleeve must be watertight")

    mesh.write_obj(obj_path)
    mesh.write_stl(stl_path)
    mesh.write_json(json_path)

    stl = stl_path.read_bytes()
    triangle_count = int.from_bytes(stl[80:84], "little")
    if len(stl) != 84 + 50 * triangle_count:
        raise RuntimeError("binary STL length does not match triangle count")
    if triangle_count != mesh.triangle_count:
        raise RuntimeError("STL triangle count does not match the mesh")

    return {
        "vertex_count": mesh.vertex_count,
        "triangle_count": mesh.triangle_count,
        "watertight": mesh.is_watertight,
        "surface_area": mesh.surface_area,
        "bounds": [list(mesh.bounds[0]), list(mesh.bounds[1])],
        "panels": [panel.name for panel in mesh.panels],
        "obj": str(obj_path),
        "stl": str(stl_path),
        "json": str(json_path),
    }


def main() -> None:
    metrics = build_sleeve_panel(Path("out") / "sleeve_panel")
    print(metrics)


if __name__ == "__main__":
    main()
