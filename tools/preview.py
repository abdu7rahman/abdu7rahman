#!/usr/bin/env python3
"""Render README.md to a page that looks close to how GitHub will show it.

Not a substitute for looking at the real profile, but it catches the things
worth catching before pushing: a plate that overflows the column, a theme that
only works in one direction, a table that wraps badly. GitHub's readable width
is 1012px inside the content column, which is narrower than the plates are
authored at, so this is also where you find out that a 1231px plate gets scaled
down to 88% and its 10px labels land at 9.

    python3 tools/preview.py && node tools/shot_preview.js

Writes build/preview.html, which is gitignored.
"""
import os
import re
import sys

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build")
os.makedirs(OUT, exist_ok=True)

src = open(os.path.join(ROOT, "README.md")).read()

# <picture> with a dark <source> is how GitHub themes an image, but the markdown
# library passes it through as a raw block and the browser then honours the
# reader's OS setting rather than the class on the page. Since the preview needs
# to force a theme, rewrite each <picture> down to the one <img> that theme
# would actually pick.
def pick(theme):
    def sub(m):
        block = m.group(0)
        if theme == "dark":
            dark = re.search(r'srcset="([^"]+)"', block)
            if dark:
                return re.sub(r'src="[^"]+"', 'src="%s"' % dark.group(1),
                              re.search(r'<img[^>]+>', block).group(0))
        img = re.search(r'<img[^>]+>', block)
        return img.group(0) if img else block
    return sub


CSS = """
:root { color-scheme: light dark }
body { margin:0; background:var(--bg); color:var(--fg);
  font:16px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif }
.wrap { max-width:1012px; margin:0 auto; padding:32px 16px 64px }
img { max-width:100%; box-sizing:border-box }
h2 { font-size:1.5em; font-weight:600; padding-bottom:.3em;
  border-bottom:1px solid var(--rule); margin-top:24px; margin-bottom:16px }
hr { height:.25em; padding:0; margin:24px 0; background:var(--rule); border:0 }
table { border-collapse:collapse; border-spacing:0; display:block;
  width:max-content; max-width:100%; overflow:auto; margin-bottom:16px }
th,td { padding:6px 13px; border:1px solid var(--rule) }
tr:nth-child(2n) { background:var(--alt) }
blockquote { margin:0 0 16px; padding:0 1em; color:var(--mut);
  border-left:.25em solid var(--rule) }
code { background:var(--alt); padding:.2em .4em; border-radius:6px; font-size:85% }
pre { background:var(--alt); padding:16px; border-radius:6px; overflow:auto; line-height:1.45 }
pre code { background:none; padding:0 }
details { margin-bottom:16px } summary { cursor:pointer; font-weight:600 }
a { color:var(--link); text-decoration:none } a:hover { text-decoration:underline }
sub { font-size:85%; color:var(--mut) }
.light { --bg:#fff; --fg:#1f2328; --mut:#59636e; --rule:#d1d9e0; --alt:#f6f8fa; --link:#0969da }
.dark  { --bg:#0d1117; --fg:#f0f6fc; --mut:#9198a1; --rule:#3d444d; --alt:#151b23; --link:#4493f8 }
"""

for theme in ("light", "dark"):
    # Comments first, and the order is not arbitrary. The comment at the top of
    # the README explains what the <picture> tags do, so it contains the literal
    # string "<picture>"; substituting pictures first matched from inside the
    # comment through to the real hero's </picture>, ate the comment's
    # terminator, and rendered half the explanation as body text.
    body = re.sub(r'<!--.*?-->', '', src, flags=re.S)
    body = re.sub(r'<picture>.*?</picture>', pick(theme), body, flags=re.S)
    # GitHub processes markdown inside a block-level HTML tag when a blank line
    # separates it, which is why the systems table is written the way it is.
    # python-markdown wants to be told, so the preview says so explicitly --
    # without this every cell renders its own asterisks.
    # The table itself has to be marked too, not just the cells: md_in_html only
    # descends into elements that opted in, so marking <td> alone left the
    # extension never looking inside the <table> that contains them.
    body = re.sub(r'<(table|tr|td|th)( [^>]*)?>', lambda m: '<%s%s markdown="block">'
                  % (m.group(1), m.group(2) or ''), body)
    html = markdown.markdown(body, extensions=["tables", "md_in_html"])
    page = ("<!doctype html><meta charset='utf-8'><base href='../'>"
            "<title>README preview — %s</title><style>%s</style>"
            "<body class='%s'><div class='wrap'>%s</div>"
            % (theme, CSS, theme, html))
    path = os.path.join(OUT, "preview-%s.html" % theme)
    open(path, "w").write(page)
    print("wrote", os.path.relpath(path, ROOT))
