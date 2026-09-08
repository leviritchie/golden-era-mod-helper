"""Build a static documentation website for GitHub Pages.

GitHub Pages can only serve files. It cannot run the Python studio or write
sandbox JSON for a visitor. This builder turns the markdown docs plus a few
read-only catalogs into HTML.
"""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path
from typing import Any

from .hook_catalog import families
from .markdown import markdown_to_html
from .paths import DATA_DIR, DOCS_DIR, HELPER_ROOT, STUDIO_DIR
from .proof import SILENT_MISS_QUESTIONS, TIERS

REPO_URL = "https://github.com/leviritchie/golden-era-mod-helper"
SITE_URL = "https://leviritchie.github.io/golden-era-mod-helper/"


def _index() -> list[dict[str, Any]]:
    return json.loads((DATA_DIR / "components_index.json").read_text(encoding="utf-8-sig"))


def _rewrite_doc_hrefs(markup: str) -> str:
    markup = re.sub(r'href="([^"]+)\.md"', r'href="\1.html"', markup)
    return markup


def _nav(current: str) -> str:
    items = [
        ("index.html", "Overview"),
        ("20_glossary.html", "Glossary"),
        ("21_tools.html", "What the tools do"),
        ("18_getting_started.html", "Getting started"),
        ("PRINCIPLES.html", "Principles"),
    ]
    for row in _index():
        href = Path(row["file"]).with_suffix(".html").name
        title = row["title"]
        if href in {item[0] for item in items}:
            continue
        items.append((href, title))
    items.extend(
        [
            ("hooks.html", "Hook catalog"),
            ("silent.html", "Silent miss doctor"),
            ("proof.html", "Proof labels"),
            ("writers.html", "Practice file writers"),
        ]
    )
    links: list[str] = []
    for href, title in items:
        current_attr = ' aria-current="page"' if href == current else ""
        links.append(f'<a href="{html.escape(href)}"{current_attr}>{html.escape(title)}</a>')
    links.append(f'<a href="{html.escape(REPO_URL)}">GitHub repository</a>')
    return "\n      ".join(links)


def _page(title: str, current: str, body: str, *, extra_class: str = "doc") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} · Golden Era Mod Helper</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="top">
    <div>
      <p class="kicker">Olden Era modding docs · examples from the Golden Era mod</p>
      <h1>Golden Era Mod Helper</h1>
    </div>
    <p class="sandbox-note">You can read this in a browser with no Python and no game install. Forms that write files still need a local clone.</p>
  </header>
  <div class="shell">
    <nav class="nav" aria-label="Documentation">
      {_nav(current)}
    </nav>
    <main class="app">
      <article class="{extra_class}">
        {body}
      </article>
    </main>
  </div>
</body>
</html>
"""


def _home_body() -> str:
    cards = []
    for row in _index()[:3]:
        href = Path(row["file"]).with_suffix(".html").name
        cards.append(
            f'<article class="card"><h3><a href="{html.escape(href)}">{html.escape(row["title"])}</a></h3>'
            f"<p>Open this page next if you have never used the kit.</p></article>"
        )
    return f"""
        <p class="lede">This is a public documentation website for people who have never modded <em>Heroes of Might and Magic: Olden Era</em>. Olden Era is the game. Golden Era is an example <em>mod</em> for that game. These pages show how Golden Era was made; the same jobs apply to other Olden Era mods. You do not need Python, Steam, or a clone to read this site.</p>
        <p>Start here, in this order:</p>
        <div class="grid">{"".join(cards)}</div>
        <h2>What this site can do</h2>
        <p>GitHub can host a small website from this repository. That product is called <strong>GitHub Pages</strong>. It can show these articles, the hook catalog, and the silent-miss questions.</p>
        <h2>What this site cannot do</h2>
        <p>GitHub Pages is a stack of HTML files. It has no Python process and no folder on <em>your</em> computer to write into. The Focus assigner, faction scaffold, and other writers still need a clone:</p>
        <pre><code>git clone {html.escape(REPO_URL)}.git
cd golden-era-mod-helper
python cli.py studio --port 8777</code></pre>
        <p>Then open <code>http://127.0.0.1:8777</code> on your machine. Details: <a href="writers.html">Practice file writers</a>.</p>
        <p>This website: <a href="{html.escape(SITE_URL)}">{html.escape(SITE_URL)}</a></p>
        <p>Public clone: <a href="{html.escape(REPO_URL)}">{html.escape(REPO_URL)}</a></p>
"""


def _writers_body() -> str:
    return """
        <h2>Practice file writers</h2>
        <p class="lede">The local studio and <code>python cli.py</code> commands write overlay-review JSON into a <code>sandbox</code> folder inside a clone. That cannot happen on this GitHub Pages site. Those files are checklists for a packer you own. They are not Core.zip rows.</p>
        <p>A GitHub Wiki would have the same limit: it can store markdown pages, but it cannot run the helper or install a mod.</p>
        <h3>What to clone for</h3>
        <ul>
          <li>Focus ability assigner</li>
          <li>Faction scaffold</li>
          <li>Billboard vs mesh plan</li>
          <li>Hero ability grant plan</li>
          <li>Building / town plan</li>
          <li>Faction law override</li>
        </ul>
        <p>Field-by-field help for those tools lives in <a href="21_tools.html">What every tool does</a>. After you clone:</p>
        <pre><code>python cli.py studio --port 8777</code></pre>
        <p>Leave that terminal open and use the local website. Closing the terminal stops it.</p>
"""


def _hooks_body() -> str:
    blocks: list[str] = [
        "<h2>Hook catalog</h2>",
        "<p class=\"lede\">A hook is a plugin patch on a method that already exists in the game. Live method names look like random letters and change after game updates. This catalog names families and what not to do. Golden Era class names are examples from one plugin, not a public API.</p>",
    ]
    for family in families():
        hooks = family.get("hooks") or []
        items = "".join(
            f"<li><strong>{html.escape(str(hook.get('name') or ''))}</strong> — "
            f"{html.escape(str(hook.get('do') or ''))} Do not: "
            f"{html.escape(str(hook.get('doNot') or ''))}</li>"
            for hook in hooks
        )
        blocks.append(
            "<article class=\"card\">"
            f"<h3>{html.escape(str(family.get('title') or family.get('id') or 'Family'))}</h3>"
            f"<p>Layer: {html.escape(str(family.get('layer') or ''))}. "
            f"When: {html.escape(str(family.get('when') or ''))}</p>"
            f"<p>Symbols: <code>{html.escape(str(family.get('symbolsClass') or ''))}</code></p>"
            f"<ul class=\"plain\">{items}</ul>"
            "</article>"
        )
    return "\n".join(blocks)


def _silent_body() -> str:
    items = []
    for row in SILENT_MISS_QUESTIONS:
        items.append(
            "<details class=\"card\">"
            f"<summary>{html.escape(row['prompt'])}</summary>"
            f"<p>{html.escape(row['diagnosis'])}</p>"
            "</details>"
        )
    return (
        "<h2>Silent miss doctor</h2>"
        "<p class=\"lede\">Use this when you believe the data is present but the player still sees nothing. Open the sentence that matches. The answer is a diagnosis, not a patch to paste blindly.</p>"
        + "".join(items)
    )


def _proof_body() -> str:
    rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(tier['id'])}</code></td>"
        f"<td>{html.escape(tier['label'])}</td>"
        f"<td>{html.escape(tier['means'])}</td>"
        f"<td>{html.escape(tier['doesNotMean'])}</td>"
        "</tr>"
        for tier in TIERS
    )
    return (
        "<h2>Proof labels</h2>"
        "<p class=\"lede\">These labels stop you from saying “it works” when you only meant “a file exists.”</p>"
        "<table><tr><th>Id</th><th>Label</th><th>Means</th><th>Does not mean</th></tr>"
        f"{rows}</table>"
    )


def build_site(output_dir: Path | None = None) -> Path:
    """Write a static site into ``output_dir`` (default ``./site`` next to cli.py)."""
    dest = (output_dir or (HELPER_ROOT / "site")).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(STUDIO_DIR / "static" / "styles.css", dest / "styles.css")
    (dest / ".nojekyll").write_text("", encoding="utf-8")

    pages: dict[str, tuple[str, str, str]] = {
        "index.html": ("Overview", "index.html", _home_body()),
        "writers.html": ("Practice file writers", "writers.html", _writers_body()),
        "hooks.html": ("Hook catalog", "hooks.html", _hooks_body()),
        "silent.html": ("Silent miss doctor", "silent.html", _silent_body()),
        "proof.html": ("Proof labels", "proof.html", _proof_body()),
    }
    principles = (HELPER_ROOT / "PRINCIPLES.md").read_text(encoding="utf-8")
    pages["PRINCIPLES.html"] = (
        "Principles",
        "PRINCIPLES.html",
        _rewrite_doc_hrefs(markdown_to_html(principles)),
    )
    extra = "doc"
    for filename, (title, current, body) in pages.items():
        cls = "stack" if filename == "index.html" else extra
        (dest / filename).write_text(
            _page(title, current, body, extra_class=cls),
            encoding="utf-8",
            newline="\n",
        )

    for row in _index():
        source_path = DOCS_DIR / row["file"]
        markup = _rewrite_doc_hrefs(markdown_to_html(source_path.read_text(encoding="utf-8")))
        filename = source_path.with_suffix(".html").name
        (dest / filename).write_text(
            _page(row["title"], filename, markup),
            encoding="utf-8",
            newline="\n",
        )
        alias = f"{row['id']}.html"
        if alias != filename:
            (dest / alias).write_text(
                _page(row["title"], filename, markup),
                encoding="utf-8",
                newline="\n",
            )
    return dest


if __name__ == "__main__":
    print(build_site())
