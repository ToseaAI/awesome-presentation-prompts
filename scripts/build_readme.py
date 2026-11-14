#!/usr/bin/env python3
"""Generate README.md from prompts.json.

Single source of truth: ../prompts.json (relative to this script). Run it after
editing prompts.json or images/:

    python scripts/build_readme.py

Standard library only.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "prompts.json"

REPO_URL = "https://github.com/ToseaAI/awesome-presentation-prompts"
LIBRARY_URL = "https://tosea.ai/prompts/presentations"
TOSEA_URL = "https://tosea.ai"

# Display order, heading and one-line description of each scenario.
SCENARIOS = [
    ("marketing", "Marketing", "Launch decks, monthly marketing reports, competitive analysis and sales enablement."),
    ("consulting", "Consulting", "Strategy frameworks in the layouts consulting decks use: matrices, issue trees, answer-first storylines."),
    ("business", "Business", "QBRs, board decisions, dashboards and reviews."),
    ("finance", "Finance", "Pitch decks, investor updates and financial reviews."),
    ("research", "Research", "Conference talks, defenses, journal clubs and lectures."),
    ("design", "Design", "Themes, chart styling and slide redesign."),
]
RETURNS = {
    "deck": "Full deck",
    "slide": "Single slide",
    "outline": "Outline",
    "restyle": "Restyle",
    "notes": "Speaker notes",
    "other": "Add-on rule",
}
STYLE_NAMES = {"mckinsey": "McKinsey", "bcg": "BCG", "bain": "Bain", "pwc": "PwC", "deloitte": "Deloitte"}
STYLE_NOTE = (
    'Names such as "McKinsey-style" describe a slide layout convention. '
    "This project is not affiliated with or endorsed by any of the firms named."
)


def fence(text: str) -> str:
    """A code fence longer than any run of backticks inside the prompt."""
    ticks = "```"
    while ticks in text:
        ticks += "`"
    return f"{ticks}text\n{text}\n{ticks}"


def meta_line(entry: dict) -> str:
    parts = [f"`{entry['id']}`", RETURNS[entry["returns"]]]
    image = entry["image"]
    if image and image.get("slides") and image["slides"] > 1:
        parts.append(f"{image['slides']} slides")
    if entry["style"]:
        parts.append(f"{STYLE_NAMES[entry['style']]}-style")
    return " · ".join(parts)


def entry_block(entry: dict, number: int) -> str:
    lines = [
        f'<a id="{entry["anchor"]}"></a>',
        f"### {number:02d}. {entry['title']}",
        "",
        meta_line(entry),
        "",
        entry["summary"],
        "",
    ]
    image = entry["image"]
    if image:
        label = "Generated in Tosea" if image["generatedInTosea"] else "Example slide"
        alt = html.escape(image["alt"], quote=True)
        lines += [
            f'<p align="center"><a href="{image["path"]}"><img src="{image["path"]}" width="640" alt="{alt}"/></a><br><sub>{label}</sub></p>',
            "",
        ]
    lines += [
        "<details>",
        "<summary><b>Prompt</b> (click to expand, then use the copy button)</summary>",
        "",
        fence(entry["prompt"]),
        "",
        "</details>",
        "",
    ]
    links = [f"**[→ Open on Tosea]({entry['toseaUrl']})**"]
    if entry["pack"]:
        links.append(f"part of [{entry['pack']['title']}]({entry['pack']['url']})")
    links.append(f"from the guide [{entry['guide']['title']}]({entry['guide']['url']})")
    lines += [" · ".join(links), "", "---", ""]
    return "\n".join(lines)


def featured_table(entries: list[dict], featured_ids: list[str]) -> str:
    by_id = {e["id"]: e for e in entries}
    cells = []
    for pid in featured_ids:
        e = by_id[pid]
        alt = html.escape(e["image"]["alt"], quote=True)
        cells.append(
            f'<td align="center" width="25%"><a href="#{e["anchor"]}"><img src="{e["image"]["path"]}" width="220" alt="{alt}"/></a>'
            f"<br><sub>{html.escape(e['title'])}</sub></td>"
        )
    return '<table align="center"><tr>\n' + "\n".join(cells) + "\n</tr></table>"


def build(data: dict) -> str:
    entries = data["entries"]
    total = len(entries)
    with_image = sum(1 for e in entries if e["image"])
    by_scenario = {slug: [e for e in entries if e["scenario"] == slug] for slug, _, _ in SCENARIOS}
    missing = {e["scenario"] for e in entries} - set(by_scenario)
    if missing:
        raise SystemExit(f"prompts.json has scenarios that SCENARIOS does not list: {sorted(missing)}")

    out = [
        '<h1 align="center">Awesome Presentation Prompts</h1>',
        "",
        '<p align="center"><i>Prompts for PowerPoint decks, with the slides they make.</i></p>',
        "",
        '<p align="center">',
        '  <a href="LICENSE"><img alt="License: CC BY 4.0" src="https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg"></a>',
        f'  <a href="{LIBRARY_URL}"><img alt="Library on Tosea.ai" src="https://img.shields.io/badge/Library-Tosea.ai-000000?style=flat"></a>',
        f'  <a href="{REPO_URL}/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/ToseaAI/awesome-presentation-prompts?style=flat&color=yellow"></a>',
        f'  <a href="{REPO_URL}/network/members"><img alt="GitHub forks" src="https://img.shields.io/github/forks/ToseaAI/awesome-presentation-prompts?style=flat&color=blue"></a>',
        "</p>",
        "",
        f"{total} copy-ready prompts for building presentation decks with AI, grouped by what the deck is for. "
        f"{with_image} of them come with an example slide, so you can see the kind of result before you run one.",
        "",
        "The prompts are plain text, so they work in ChatGPT, Claude, Gemini and Copilot. They come from the guides on the "
        f"[Tosea]({TOSEA_URL}) blog. Tosea turns a prompt and your source files into an editable deck.",
        "",
        f"> {total} prompts across {len(SCENARIOS)} scenarios. [→ Search the library on Tosea]({LIBRARY_URL})",
        "",
        "## Featured",
        "",
        featured_table(entries, data["featured"]),
        "",
        "## Table of Contents",
        "",
    ]
    for slug, name, _ in SCENARIOS:
        group = by_scenario[slug]
        shown = sum(1 for e in group if e["image"])
        out.append(f"- [{name}](#{slug}) · *{len(group)} prompts, {shown} with an example slide*")
    out += [
        "- [How to use a prompt](#how-to-use-a-prompt)",
        "- [Contributing](#contributing)",
        "- [License](#license)",
        "",
        "## How to use a prompt",
        "",
        "1. Pick a prompt and copy it. Replace anything in `[brackets]` with your own details.",
        "2. Attach the material the prompt refers to: a brief, a report, notes or screenshots. A prompt with no source material gets a generic deck.",
        "3. Run it. In Tosea you review the outline first, then generate the slides and export an editable PowerPoint file.",
        "",
        "Each entry says what the prompt returns: a full deck, a single slide, an outline, a restyle of existing slides, "
        "speaker notes, or an add-on rule you paste after another prompt. "
        '"Generated in Tosea" under a slide means it came from running that exact prompt in Tosea. '
        '"Example slide" means it illustrates the prompt but was made another way.',
        "",
    ]
    for slug, name, blurb in SCENARIOS:
        group = by_scenario[slug]
        out += [f'<a id="{slug}"></a>', f"## {name}", "", blurb, ""]
        if any(e["style"] for e in group):
            out += [f"> {STYLE_NOTE}", ""]
        if slug == "marketing" and data.get("sampleNote"):
            out += [f"> {data['sampleNote']}", ""]
        for number, entry in enumerate(group, start=1):
            out.append(entry_block(entry, number))
    out += [
        "## Contributing",
        "",
        "Found a prompt that produces a better deck? Open an issue with the prompt, what you attached, and one slide it produced. "
        "**Only edit `prompts.json`** in pull requests: this README is generated by `scripts/build_readme.py`. "
        "See [CONTRIBUTING.md](CONTRIBUTING.md).",
        "",
        "## License",
        "",
        "The prompts and example slides are released under [CC BY 4.0](LICENSE). Use them anywhere, including commercially; credit Tosea with a link.",
        "",
        f'<p align="center"><sub>Edition {data["edition"]} · {data["updated"]} · {total} prompts · Maintained by '
        f'<a href="{TOSEA_URL}">Tosea.ai</a> · Generated from <code>prompts.json</code>.</sub></p>',
        "",
    ]
    return "\n".join(out)


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    for entry in data["entries"]:
        image = entry["image"]
        if image and not (ROOT / image["path"]).is_file():
            raise SystemExit(f"{entry['id']}: {image['path']} is missing")
    (ROOT / "README.md").write_text(build(data), encoding="utf-8")
    print(f"wrote README.md with {len(data['entries'])} prompts")


if __name__ == "__main__":
    main()
