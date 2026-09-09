"""Project version metadata in pyproject.toml."""

from __future__ import annotations

import re
from pathlib import Path

_VERSION_LINE = re.compile(r'(?m)^version = "([^"]+)"')


def test_pyproject_version_is_semver_like() -> None:
    text = Path("pyproject.toml").read_text(encoding="utf-8")
    match = _VERSION_LINE.search(text)
    assert match is not None
    version = match.group(1)
    assert isinstance(version, str)
    parts = version.split(".")
    assert len(parts) >= 2
    assert all(part.isdigit() for part in parts[:2])
