from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "cadflow"
SKILL_FILE = SKILL_ROOT / "SKILL.md"
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REMOVED_TERMS = (
    "cadflow-harness",
    "build_model(",
    "code/model.py",
    "validate_model",
    "cad_review",
    "PRODUCT_SPEC",
    "TEXT_TO_CAD",
    "deepagents",
    "localhost:5678",
    "localhost:8765",
)


def _frontmatter() -> dict[str, object]:
    text = SKILL_FILE.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    assert match, "SKILL.md must start with YAML frontmatter"
    data = yaml.safe_load(match.group(1))
    assert isinstance(data, dict)
    return data


def _skill_files() -> list[Path]:
    return [path for path in SKILL_ROOT.rglob("*") if path.is_file()]


def test_skill_frontmatter_matches_agent_skills_spec() -> None:
    data = _frontmatter()
    name = data["name"]
    description = data["description"]
    assert name == "cadflow"
    assert SKILL_ROOT.name == name
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
    assert 1 <= len(name) <= 64
    assert isinstance(description, str) and 1 <= len(description) <= 1024
    assert data["license"] == "MIT"
    metadata = data["metadata"]
    assert metadata["cadflow_version"] == "0.2.0"
    assert metadata["pypi"] == "https://pypi.org/project/cadflow/0.2.0/"


def test_skill_is_self_contained() -> None:
    files = _skill_files()
    assert SKILL_FILE in files
    markdown_files = [path for path in files if path.suffix == ".md"]
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            assert resolved.exists(), f"{path} links to missing {target}"
            assert resolved == SKILL_ROOT or SKILL_ROOT in resolved.parents, (
                f"{path} points outside the skill: {target}"
            )


def test_skill_does_not_embed_harness_contracts() -> None:
    for path in _skill_files():
        if path.suffix not in {".md", ".py", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for term in REMOVED_TERMS:
            assert term.lower() not in lowered, f"{path} still mentions {term}"


def test_openai_metadata_is_optional_and_local() -> None:
    metadata_path = SKILL_ROOT / "agents" / "openai.yaml"
    payload = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    assert payload["interface"]["display_name"] == "CadFlow"
    assert "$cadflow" in payload["interface"]["default_prompt"]


def test_host_discovery_links_point_at_the_same_skill() -> None:
    for relative in (
        Path(".agents/skills/cadflow"),
        Path(".pi/skills/cadflow"),
        Path(".claude/skills/cadflow"),
    ):
        path = REPO_ROOT / relative
        assert path.is_symlink(), f"{relative} should be a symlink"
        assert path.resolve() == SKILL_ROOT


def test_examples_are_plain_python_entry_points() -> None:
    examples = sorted((SKILL_ROOT / "examples").glob("*.py"))
    assert {path.name for path in examples} == {
        "mounting_plate.py",
        "hinge_assembly.py",
    }
    for path in examples:
        source = path.read_text(encoding="utf-8")
        assert "import cadflow as cad" in source
        assert "def main() -> None:" in source
        assert "if __name__ == " in source
        assert "build_model(" not in source
