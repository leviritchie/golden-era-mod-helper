"""Small Markdown-to-HTML converter. No third-party dependency."""

from __future__ import annotations

import html
import re


def markdown_to_html(source: str) -> str:
    lines = source.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    in_code = False
    in_list = False
    in_table = False
    table_rows: list[list[str]] = []
    fence_lang = ""

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def close_table() -> None:
        nonlocal in_table, table_rows
        if not in_table:
            return
        out.append("<table>")
        for index, cells in enumerate(table_rows):
            tag = "th" if index == 0 else "td"
            out.append("<tr>" + "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in cells) + "</tr>")
        out.append("</table>")
        in_table = False
        table_rows = []

    for raw in lines:
        if raw.startswith("```"):
            close_list()
            close_table()
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                fence_lang = html.escape(raw[3:].strip())
                cls = f' class="lang-{fence_lang}"' if fence_lang else ""
                out.append(f"<pre{cls}><code>")
                in_code = True
            continue
        if in_code:
            out.append(html.escape(raw))
            continue
        if re.match(r"^\s*\|.*\|\s*$", raw) and not re.match(r"^\s*\|?\s*-+", raw):
            close_list()
            cells = [c.strip() for c in raw.strip().strip("|").split("|")]
            if all(set(c) <= set("-: ") and c for c in cells):
                continue
            in_table = True
            table_rows.append(cells)
            continue
        if in_table:
            close_table()
        heading = re.match(r"^(#{1,6})\s+(.*)$", raw)
        if heading:
            close_list()
            level = len(heading.group(1))
            out.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
            continue
        if re.match(r"^\s*[-*]\s+", raw):
            if not in_list:
                out.append("<ul>")
                in_list = True
            item = re.sub(r"^\s*[-*]\s+", "", raw)
            out.append(f"<li>{_inline(item)}</li>")
            continue
        close_list()
        if not raw.strip():
            continue
        out.append(f"<p>{_inline(raw)}</p>")
    close_list()
    close_table()
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def _inline(text: str) -> str:
    escaped = html.escape(text)

    def code_repl(match: re.Match[str]) -> str:
        return f"<code>{match.group(1)}</code>"

    escaped = re.sub(r"`([^`]+)`", code_repl, escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>',
        escaped,
    )
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped
