"""MkDocs site identity and published URL."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_cname_is_custom_domain() -> None:
    text = (ROOT / "mkdocs" / "CNAME").read_text(encoding="utf-8").strip()
    assert text == "spider-frameworks.thelupaxaproject.org"


def test_mkdocs_yml_identity() -> None:
    text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert "site_name: Spider Frameworks" in text
    assert "site_url: https://spider-frameworks.thelupaxaproject.org/" in text
    assert "repo_name: lupaxa-spider-toolbox/spider-frameworks" in text
    assert "counter_dev_id: ef410665-76d4-43fe-9e91-53f26ed1004b" in text
    assert "start_year" not in text


def test_mkdocs_pins_in_pyproject() -> None:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "mkdocs==1.6.1" in text
    assert "mkdocs-material==9.7.7" in text


def test_root_requirements_has_mkdocs_pins() -> None:
    text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "mkdocs==1.6.1" in text
    assert "mkdocs-material==9.7.7" in text


def test_home_states_not_a_library() -> None:
    text = (ROOT / "mkdocs" / "index.md").read_text(encoding="utf-8")
    assert "not an installable crawler library" in text.lower()


def test_example_recipe_headings() -> None:
    text = (ROOT / "mkdocs" / "examples.md").read_text(encoding="utf-8")
    for heading in (
        "## Start with a host",
        "## Set a user-agent",
        "## Limit concurrency",
        "## Stop with Ctrl-C",
    ):
        assert heading in text


def test_readme_links_recipes() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "https://spider-frameworks.thelupaxaproject.org/" in text
    assert "examples/#start-with-a-host" in text
    assert "examples/#set-a-user-agent" in text
    assert "examples/#limit-concurrency" in text
    assert "examples/#stop-with-ctrl-c" in text
