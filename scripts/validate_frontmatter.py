#!/usr/bin/env python3
"""
validate_frontmatter.py — Cookbook frontmatter validator.

Validates YAML frontmatter on every Markdown file under docs/patterns/ and
docs/case-studies/.

Required fields, all chapters:
    - title (str)
    - status (str)
    - last_reviewed (date, ISO 8601)
    - spec_version (str)
    - contributors (list)

Pattern-specific:
    - version (str, semver)
    - status in {draft, stable, withdrawn, superseded}
    - domains (list)
    - platforms_tested (list)

Case-study-specific:
    - status in {published, draft}
    - attribution in {attributed, industry-attributed, anonymized}

Usage:
    python3 scripts/validate_frontmatter.py
    python3 scripts/validate_frontmatter.py --quiet
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[\w\.]+)?$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PATTERN_STATUS = {"draft", "stable", "withdrawn", "superseded"}
CASESTUDY_STATUS = {"published", "draft"}
CASESTUDY_ATTRIBUTION = {"attributed", "industry-attributed", "anonymized"}


@dataclass
class ValidationResult:
    path: Path
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def extract_frontmatter(text: str) -> dict | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def is_iso_date(value) -> bool:
    if isinstance(value, date):
        return True
    return isinstance(value, str) and bool(ISO_DATE_RE.match(value))


def validate_common(fm: dict, errors: list[str]) -> None:
    if not isinstance(fm.get("title"), str) or not fm["title"].strip():
        errors.append("missing or empty `title`")
    if not is_iso_date(fm.get("last_reviewed")):
        errors.append(f"`last_reviewed` must be ISO date, got: {fm.get('last_reviewed')!r}")
    if not isinstance(fm.get("spec_version"), str) or not fm["spec_version"].strip():
        errors.append("missing or empty `spec_version`")
    if not isinstance(fm.get("contributors"), list) or not fm["contributors"]:
        errors.append("`contributors` must be a non-empty list")


def validate_pattern(fm: dict, errors: list[str]) -> None:
    if fm.get("status") not in PATTERN_STATUS:
        errors.append(f"`status` must be one of {sorted(PATTERN_STATUS)}, got: {fm.get('status')!r}")
    version = fm.get("version")
    if not isinstance(version, str) or not SEMVER_RE.match(version):
        errors.append(f"`version` must be semver, got: {version!r}")
    for key in ("domains", "platforms_tested"):
        if not isinstance(fm.get(key), list) or not fm[key]:
            errors.append(f"`{key}` must be a non-empty list")


def validate_case_study(fm: dict, errors: list[str]) -> None:
    if fm.get("status") not in CASESTUDY_STATUS:
        errors.append(f"`status` must be one of {sorted(CASESTUDY_STATUS)}, got: {fm.get('status')!r}")
    if fm.get("attribution") not in CASESTUDY_ATTRIBUTION:
        errors.append(
            f"`attribution` must be one of {sorted(CASESTUDY_ATTRIBUTION)}, got: {fm.get('attribution')!r}"
        )


def validate_file(path: Path) -> ValidationResult:
    result = ValidationResult(path=path)
    text = path.read_text(encoding="utf-8")
    fm = extract_frontmatter(text)
    if fm is None:
        result.errors.append("missing or malformed frontmatter")
        return result
    validate_common(fm, result.errors)
    if "patterns" in path.parts:
        validate_pattern(fm, result.errors)
    elif "case-studies" in path.parts:
        validate_case_study(fm, result.errors)
    return result


def find_targets(repo_root: Path) -> list[Path]:
    targets = []
    for sub in ("docs/patterns", "docs/case-studies"):
        d = repo_root / sub
        if not d.exists():
            continue
        for p in sorted(d.glob("*.md")):
            if p.name.startswith("_") or p.name == "INDEX.md":
                continue
            targets.append(p)
    return targets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    args = parser.parse_args()

    targets = find_targets(args.root)
    if not targets:
        print("No pattern or case study files found.", file=sys.stderr)
        return 1

    failures = 0
    for path in targets:
        rel = path.relative_to(args.root)
        result = validate_file(path)
        if result.ok:
            if not args.quiet:
                print(f"OK    {rel}")
        else:
            failures += 1
            print(f"FAIL  {rel}")
            for err in result.errors:
                print(f"      - {err}")

    print(f"\n{len(targets)} files checked, {failures} failed.")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
