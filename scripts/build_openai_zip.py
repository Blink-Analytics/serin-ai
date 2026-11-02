"""Build the OpenAI (Codex / ChatGPT) plugin upload archive.

Assembles dist/serin-mcp-<version>.zip from openai/plugin.json, openai/mcp.json,
assets/icon.png and the shared skills/ folder. The archive layout matches what
the OpenAI plugin portal expects:

    serin-mcp/plugin.json
    serin-mcp/mcp.json
    serin-mcp/assets/icon.png
    serin-mcp/skills/<name>/SKILL.md

Usage: python scripts/build_openai_zip.py
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFIX = "serin-mcp"


def main() -> int:
    manifest = json.loads((ROOT / "openai" / "plugin.json").read_text(encoding="utf-8"))
    version = manifest["version"]

    claude_version = json.loads(
        (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    ).get("version")
    if claude_version != version:
        print(
            f"warning: openai/plugin.json is {version} but "
            f".claude-plugin/plugin.json is {claude_version}",
            file=sys.stderr,
        )

    files: list[tuple[Path, str]] = [
        (ROOT / "openai" / "plugin.json", "plugin.json"),
        (ROOT / "openai" / "mcp.json", "mcp.json"),
        (ROOT / "assets" / "icon.png", "assets/icon.png"),
    ]
    for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
        files.append((skill, skill.relative_to(ROOT).as_posix()))

    missing = [str(src) for src, _ in files if not src.is_file()]
    if missing:
        print("missing files:\n  " + "\n  ".join(missing), file=sys.stderr)
        return 1

    out = ROOT / "dist" / f"{PREFIX}-{version}.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src, arcname in files:
            zf.write(src, f"{PREFIX}/{arcname}")

    print(f"wrote {out.relative_to(ROOT)} ({len(files)} files)")
    for _, arcname in files:
        print(f"  {PREFIX}/{arcname}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
