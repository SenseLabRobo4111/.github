from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
ROBOT_FIG_DIR = ROOT / "docs" / "robot_fig"
MANIFEST_PATH = ROBOT_FIG_DIR / "gallery-manifest.json"
README_PATH = ROOT / "profile" / "README.md"

README_START = "<!-- ROBOT_FIG_GALLERY:START -->"
README_END = "<!-- ROBOT_FIG_GALLERY:END -->"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
IGNORED_FILES = {"gallery-manifest.json"}


def iter_robot_fig_images() -> list[Path]:
    return sorted(
        [
            path
            for path in ROBOT_FIG_DIR.iterdir()
            if path.is_file()
            and path.suffix.lower() in IMAGE_EXTENSIONS
            and path.name not in IGNORED_FILES
        ],
        key=lambda path: path.name.casefold(),
    )


def humanize_filename(filename: str) -> str:
    stem = Path(filename).stem
    stem = stem.replace("_", " ").replace("-", " ")
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem or "Robot figure"


def write_manifest(images: list[Path]) -> None:
    payload = {
        "images": [
            {
                "file": image.name,
                "alt": humanize_filename(image.name),
            }
            for image in images
        ]
    }
    MANIFEST_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_readme_gallery(images: list[Path]) -> str:
    if not images:
        return '<p align="center"><em>No robot_fig images available yet.</em></p>'

    columns = 3
    lines = [
        '<table align="center" width="90%" style="border-collapse: separate; border-spacing: 6px;">'
    ]

    for row_start in range(0, len(images), columns):
        row = images[row_start : row_start + columns]
        lines.append("  <tr>")

        for image in row:
            src = f"../docs/robot_fig/{quote(image.name)}"
            alt = html.escape(humanize_filename(image.name), quote=True)
            lines.append(
                '    <td width="33%" align="center" style="border: none; padding: 0;">'
            )
            lines.append(
                f'      <img src="{src}" width="100%" style="border-radius: 12px; box-shadow: 0 10px 24px rgba(102, 0, 153, 0.18); border: 1px solid #30363d;" alt="{alt}" />'
            )
            lines.append("    </td>")

        for _ in range(columns - len(row)):
            lines.append(
                '    <td width="33%" align="center" style="border: none; padding: 0;"></td>'
            )

        lines.append("  </tr>")

    lines.append("</table>")
    return "\n".join(lines)


def update_readme(images: list[Path]) -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    start = readme.find(README_START)
    end = readme.find(README_END)

    if start == -1 or end == -1 or end < start:
        raise RuntimeError("README robot gallery markers were not found.")

    generated = build_readme_gallery(images)
    replacement = f"{README_START}\n{generated}\n{README_END}"
    updated = readme[:start] + replacement + readme[end + len(README_END) :]
    README_PATH.write_text(updated, encoding="utf-8")


def main() -> None:
    images = iter_robot_fig_images()
    write_manifest(images)
    update_readme(images)


if __name__ == "__main__":
    main()
