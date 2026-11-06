"""Small static checks for the CyberWinDiagnostics GitHub Pages site."""

from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.local_files = []
        self.images_without_alt = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "img" and "alt" not in attrs:
            self.images_without_alt.append(attrs.get("src", "(unnamed image)"))
        if tag == "img" and attrs.get("src"):
            self.images.append(attrs["src"])
        for attribute in ("src", "href"):
            value = attrs.get(attribute, "")
            if value and not value.startswith(("https://", "http://", "#", "mailto:", "data:")):
                self.local_files.append(value.split("#", 1)[0].split("?", 1)[0])


def fail(message):
    print(f"FAIL {message}", file=sys.stderr)
    raise SystemExit(1)


# Themes come from the universal Cybercore chooser (600-theme registry + 12
# signature mashups, read live from cybercoretech.github.io), not a local file.
source = (SITE / "index.html").read_text(encoding="utf-8")
for needle in ("<cybercore-theme-chooser", "https://cybercoretech.github.io/kit/chooser.js", "https://cybercoretech.github.io/kit/chooser.css"):
    if needle not in source:
        fail(f"universal theme chooser is not wired in: missing {needle}")
if (SITE / "data/themes.json").exists():
    fail("docs/data/themes.json is obsolete; themes load from the shared registry")

previews = list((SITE / "assets/previews").glob("*.svg"))
if len(previews) != 8:
    fail(f"expected 8 field-screen preview images, found {len(previews)}")

page = SiteParser()
page.feed((SITE / "index.html").read_text(encoding="utf-8"))
if page.images_without_alt:
    fail("images missing alt text: " + ", ".join(page.images_without_alt))
preview_refs = {Path(value).name for value in page.images if value.startswith("assets/previews/")}
if preview_refs != {item.name for item in previews}:
    fail("the eight field-screen previews are not all referenced from the page")
for asset in page.local_files:
    if not (SITE / asset).is_file():
        fail(f"referenced local site asset is missing: {asset}")
for anchor in re.findall(r'href="#([^"]+)"', (SITE / "index.html").read_text(encoding="utf-8")):
    if anchor not in page.ids:
        fail(f"in-page link has no matching target: #{anchor}")

source_html = (SITE / "index.html").read_text(encoding="utf-8")
legacy_html = source_html.replace('href="assets/', 'href="docs/assets/')
legacy_html = legacy_html.replace('src="assets/', 'src="docs/assets/')
legacy_html = legacy_html.replace('href="styles.css"', 'href="docs/styles.css"')
legacy_html = legacy_html.replace('href="install.css"', 'href="docs/install.css"')
legacy_html = legacy_html.replace('src="app.js"', 'src="docs/app.js"')
if (ROOT / "index.html").read_text(encoding="utf-8") != legacy_html:
    fail("root Pages compatibility index is stale; regenerate it from docs/index.html")

print("PASS: universal theme chooser, 8 previews, accessible/local assets, and root Pages compatibility copy")
