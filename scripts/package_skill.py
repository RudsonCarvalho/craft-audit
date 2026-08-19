#!/usr/bin/env python3
"""Build the portable CRAFT agent-skill archive from the canonical source directory."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "craft-audit"
DIST = ROOT / "dist"
OUTPUT = DIST / "craft-audit.skill"
REQUIRED = (
    SOURCE / "SKILL.md",
    SOURCE / "references" / "profile.md",
    SOURCE / "references" / "output-schema.md",
)


def main() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.is_file()]
    if missing:
        raise SystemExit("Missing required skill files: " + ", ".join(missing))

    DIST.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(SOURCE.rglob("*")):
            if path.is_file():
                archive.write(path, Path("craft-audit") / path.relative_to(SOURCE))

    print(f"Built {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
