from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SKILL_EXAMPLES = Path(__file__).resolve().parents[1] / "skills" / "cadflow" / "examples"

cadflow = pytest.importorskip("cadflow")


def _load(name: str):
    path = SKILL_EXAMPLES / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _step_looks_real(path: Path) -> None:
    payload = path.read_bytes()
    assert path.stat().st_size > 200
    assert payload.startswith(b"ISO-10303-21")
    assert b"ENDSEC" in payload


def test_cadflow_package_is_the_selected_pypi_release() -> None:
    assert cadflow.__version__ == "0.2.0"


def test_mounting_plate_exports_reopenable_step(tmp_path: Path) -> None:
    module = _load("mounting_plate")
    metrics = module.build_mounting_plate(tmp_path)
    step_path = Path(metrics["step"])
    stl_path = Path(metrics["stl"])
    _step_looks_real(step_path)
    assert stl_path.stat().st_size > 80
    assert metrics["topology"]["solids"] == 1
    assert metrics["imported_solids"] == 1
    assert metrics["volume"] > 0.0
    assert abs(metrics["imported_volume"] - metrics["volume"]) < 1e-3

    with cadflow.Model() as model:
        imported = model.import_step(str(step_path))
        assert imported.topology["solids"] == 1
        assert abs(imported.volume - metrics["volume"]) < 1e-3


def test_hinge_assembly_exports_reopenable_step(tmp_path: Path) -> None:
    module = _load("hinge_assembly")
    metrics = module.build_hinge_assembly(tmp_path)
    step_path = Path(metrics["step"])
    _step_looks_real(step_path)
    assert metrics["solved"] is True
    assert metrics["components"] == ["base", "arm"]
    assert metrics["imported_solids"] == 2
    assert metrics["imported_volume"] > 0.0

    with cadflow.Model() as model:
        imported = model.import_step(str(step_path))
        assert imported.topology["solids"] == 2
        assert imported.volume > 0.0
