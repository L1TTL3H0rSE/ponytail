#!/usr/bin/env python3
"""Build ChatGPT-uploadable Ponytail skill archives from canonical skills/."""

from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path

SKILLS = (
    "ponytail",
    "ponytail-review",
    "ponytail-audit",
    "ponytail-debt",
    "ponytail-gain",
    "ponytail-help",
)
MAX_ZIP_BYTES = 25 * 1024 * 1024
ALLOWED_FRONTMATTER = {"name", "description"}


def display_name(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def normalize_skill_md(text: str, expected_name: str) -> str:
    if not text.startswith("---\n"):
        raise ValueError(f"{expected_name}: SKILL.md has no YAML frontmatter")

    try:
        frontmatter, body = text[4:].split("\n---", 1)
    except ValueError as exc:
        raise ValueError(f"{expected_name}: malformed YAML frontmatter") from exc

    kept: list[str] = []
    current_keep = False
    found: set[str] = set()
    for line in frontmatter.splitlines():
        if line and not line[0].isspace():
            key = line.split(":", 1)[0].strip()
            current_keep = key in ALLOWED_FRONTMATTER
            if current_keep:
                found.add(key)
        if current_keep:
            kept.append(line)

    missing = ALLOWED_FRONTMATTER - found
    if missing:
        raise ValueError(f"{expected_name}: missing frontmatter keys: {', '.join(sorted(missing))}")

    name_line = next(line for line in kept if line.startswith("name:"))
    actual_name = name_line.split(":", 1)[1].strip().strip('"\'')
    if actual_name != expected_name:
        raise ValueError(f"{expected_name}: frontmatter name is {actual_name!r}")

    description_lines: list[str] = []
    in_description = False
    for line in kept:
        if line.startswith("description:"):
            in_description = True
            tail = line.split(":", 1)[1].strip()
            if tail not in {">", "|", ">-", "|-", ""}:
                description_lines.append(tail.strip('"\''))
            continue
        if in_description:
            if line and not line[0].isspace():
                break
            description_lines.append(line.strip())
    description = " ".join(part for part in description_lines if part).strip()
    if not description:
        raise ValueError(f"{expected_name}: empty description")
    if len(description) > 1024:
        raise ValueError(f"{expected_name}: description exceeds 1024 characters")
    if "<" in description or ">" in description:
        raise ValueError(f"{expected_name}: description contains angle brackets")

    return "---\n" + "\n".join(kept) + "\n---" + body


def write_openai_metadata(skill_dir: Path, name: str) -> None:
    agents = skill_dir / "agents"
    agents.mkdir(exist_ok=True)
    (agents / "openai.yaml").write_text(
        f'interface:\n  display_name: "{display_name(name)}"\n',
        encoding="utf-8",
    )


def package_skill(source: Path, output_root: Path, name: str) -> Path:
    with tempfile.TemporaryDirectory(prefix=f"{name}-chatgpt-") as temp:
        stage = Path(temp) / name
        shutil.copytree(source, stage)

        skill_md = stage / "SKILL.md"
        skill_md.write_text(
            normalize_skill_md(skill_md.read_text(encoding="utf-8"), name),
            encoding="utf-8",
        )
        write_openai_metadata(stage, name)

        destination = output_root / name
        destination.mkdir(parents=True, exist_ok=True)
        archive = destination / "skill.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(stage.parent))

        if archive.stat().st_size > MAX_ZIP_BYTES:
            archive.unlink(missing_ok=True)
            raise ValueError(f"{name}: skill.zip exceeds 25 MiB")

        with zipfile.ZipFile(archive) as zf:
            names = set(zf.namelist())
            required = {
                f"{name}/SKILL.md",
                f"{name}/agents/openai.yaml",
            }
            missing = required - names
            if missing:
                raise ValueError(f"{name}: archive missing {', '.join(sorted(missing))}")

        return archive


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Ponytail repository root",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory (default: <root>/dist/chatgpt)",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    output = (args.output or root / "dist" / "chatgpt").resolve()
    output.mkdir(parents=True, exist_ok=True)

    for name in SKILLS:
        source = root / "skills" / name
        if not source.is_dir():
            raise SystemExit(f"missing skill directory: {source}")
        archive = package_skill(source, output, name)
        print(f"{name}: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
