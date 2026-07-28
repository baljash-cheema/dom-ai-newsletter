#!/usr/bin/env python3
"""
DOM Education Newsletter — reproducible build pipeline.

Turns one issue folder into a precise, identical-format 2-page newsletter as
both HTML (email-ready, self-contained) and PDF (print-quality US Letter):

    page 1  — DOM Education Committee content   (issues/<issue>/page1.md)
    page 2  — AI in Medical Education           (issues/<issue>/page2.md)

Shared masthead metadata (month, volume, editors, disclaimer) lives once in
issues/<issue>/issue.yaml and is merged into both pages.

Usage:
    .venv/bin/python build.py                 # builds the most recent issue
    .venv/bin/python build.py 2026-08         # builds issues/2026-08
    .venv/bin/python build.py 2026-08 --final # refuses unless every source in
                                              #   sources.yaml is verified

Outputs land in <issue>/output/:
    newsletter-<issue>.html
    newsletter-<issue>.pdf
(or with a -DRAFT suffix + watermark if any page-2 claim is unverified)

Nothing in this script invents content. It only renders what is in the page
files and reports the verification state recorded in sources.yaml. The AI page
(page 2) is the one held to the source-verification gate.
"""
from __future__ import annotations

import base64
import datetime as _dt
import mimetypes
import os
import shutil
import subprocess
import sys
from pathlib import Path


# --------------------------------------------------------------------------- #
# macOS bootstrap: WeasyPrint needs Homebrew's libs (pango/gobject/cairo) on
# the dynamic-loader path. Set it and re-exec once so a plain
# `python build.py` just works, with no env vars for the user to remember.
# --------------------------------------------------------------------------- #
def _ensure_lib_path() -> None:
    if sys.platform != "darwin" or os.environ.get("_DOM_BOOTSTRAPPED"):
        return
    lib_dir = None
    brew = shutil.which("brew")
    if brew:
        try:
            prefix = subprocess.check_output([brew, "--prefix"], text=True).strip()
            if (Path(prefix) / "lib").exists():
                lib_dir = str(Path(prefix) / "lib")
        except Exception:
            pass
    lib_dir = lib_dir or next(
        (p for p in ("/opt/homebrew/lib", "/usr/local/lib") if Path(p).exists()), None
    )
    if lib_dir:
        existing = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"{lib_dir}:{existing}" if existing else lib_dir
    os.environ["_DOM_BOOTSTRAPPED"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)


_ensure_lib_path()

import frontmatter
import markdown as md
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"
ASSETS = ROOT / "assets"
ISSUES = ROOT / "issues"

MD_EXTENSIONS = [
    "extra",        # tables, footnotes, attr_list, def_list, abbr, etc.
    "md_in_html",   # allow markdown inside raw <div> blocks (visual cards)
    "sane_lists",
    "smarty",       # typographic quotes / dashes
    "toc",
    "admonition",
]

# The page slots a full issue is built from, in printed order. Each slot is
# either an image export (page1.jpg/.jpeg/.png — used verbatim, 100% fidelity)
# or a Markdown file (page1.md) rendered through the templates. An image, if
# present, wins — that is how a committee's own Canva page 1 becomes page 1.
PAGE_SLOTS = ["page1", "page2"]
IMAGE_EXTS = (".jpg", ".jpeg", ".png")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def fail(msg: str) -> "NoReturn":  # noqa: F821
    print(f"\n  ✗ {msg}\n", file=sys.stderr)
    sys.exit(1)


def resolve_issue(arg: str | None) -> Path:
    """Resolve the issue directory from a CLI argument, or pick the latest."""
    if arg:
        cand = Path(arg)
        if not cand.is_absolute():
            cand = (ISSUES / arg) if not str(arg).startswith("issues") else (ROOT / arg)
        if not cand.exists():
            fail(f"Issue folder not found: {cand}")
        return cand
    candidates = sorted(
        p for p in ISSUES.iterdir()
        if p.is_dir() and (list(p.glob("page*.md")) or (p / "content.md").exists())
    )
    if not candidates:
        fail("No issues found. Create one with ./new-issue.sh YYYY-MM")
    return candidates[-1]


def data_uri(path: Path, mime: str | None = None) -> str:
    """Inline a file as a base64 data URI so the HTML is fully self-contained."""
    if mime is None:
        mime, _ = mimetypes.guess_type(str(path))
        mime = mime or "application/octet-stream"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


# Script fonts embedded into the CSS (self-contained output). Filename → family.
SCRIPT_FONTS = {
    "GreatVibes-subset.woff2": "Great Vibes",
    "DancingScript-subset.woff2": "Dancing Script",
}


def font_faces_css() -> str:
    """Build @font-face rules that inline any assets/fonts/*.woff2 as data URIs."""
    rules = []
    for fname, family in SCRIPT_FONTS.items():
        p = ASSETS / "fonts" / fname
        if not p.exists():
            continue
        uri = data_uri(p, mime="font/woff2")
        rules.append(
            f"@font-face {{ font-family: '{family}'; font-style: normal; "
            f"font-weight: 400 700; src: url('{uri}') format('woff2'); }}"
        )
    return "\n".join(rules) + ("\n" if rules else "")


def image_size(path: Path) -> tuple[int, int] | None:
    """Return (width, height) in px for a PNG/JPEG — no third-party dependency."""
    d = path.read_bytes()
    if d[:8] == b"\x89PNG\r\n\x1a\n":
        return int.from_bytes(d[16:20], "big"), int.from_bytes(d[20:24], "big")
    if d[:2] == b"\xff\xd8":  # JPEG: scan for a Start-Of-Frame marker
        i = 2
        while i < len(d) - 9:
            if d[i] != 0xFF:
                i += 1
                continue
            m = d[i + 1]
            if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                return int.from_bytes(d[i + 7:i + 9], "big"), int.from_bytes(d[i + 5:i + 7], "big")
            i += 2 + int.from_bytes(d[i + 2:i + 4], "big")
    return None


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def load_sources(issue_dir: Path) -> list[dict]:
    return load_yaml(issue_dir / "sources.yaml").get("sources", []) or []


def render_body(text: str) -> str:
    return md.markdown(text, extensions=MD_EXTENSIONS, output_format="html5")


def load_pages(issue_dir: Path, shared: dict) -> list[dict]:
    """Resolve each page slot to an image export or a Markdown file (image wins)."""
    slots: list[tuple[str, str, Path]] = []
    for base in PAGE_SLOTS:
        img = next((issue_dir / (base + e) for e in IMAGE_EXTS if (issue_dir / (base + e)).exists()), None)
        md = issue_dir / (base + ".md")
        if img is not None:
            slots.append((base, "image", img))
        elif md.exists():
            slots.append((base, "markdown", md))
    if not slots and (issue_dir / "content.md").exists():
        slots.append(("page2", "markdown", issue_dir / "content.md"))   # single-page fallback
    if not slots:
        fail(f"No page files (page1.* / page2.* / content.md) in {issue_dir}")

    pages: list[dict] = []
    for i, (base, kind, path) in enumerate(slots):
        if kind == "image":
            w, h = image_size(path) or (850, 1100)
            pages.append({"kind": "image", "index": i, "meta": shared,
                          "image": data_uri(path), "aspect": w / h, "show_colophon": False})
        else:
            post = frontmatter.load(path)
            pages.append({"kind": "markdown", "index": i, "meta": {**shared, **post.metadata},
                          "body": render_body(post.content),
                          # the AI page (page 2) carries the sourcing colophon; page 1 does not
                          "show_colophon": base == "page2" or path.name == "content.md"})
    return pages


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build(issue_dir: Path, final: bool) -> None:
    shared = load_yaml(issue_dir / "issue.yaml")
    pages = load_pages(issue_dir, shared)

    # Verification gate (applies to page 2's claims) ------------------------ #
    sources = load_sources(issue_dir)
    total = len(sources)
    unverified = [s for s in sources if not s.get("verified", False)]
    verified = total - len(unverified)
    all_verified = total > 0 and not unverified

    print(f"\n  Issue:    {issue_dir.name}")
    print(f"  Pages:    {len(pages)}")
    print(f"  Sources:  {verified}/{total} verified")
    if unverified:
        print("  ⚠ UNVERIFIED claims (will be watermarked DRAFT):")
        for s in unverified:
            print(f"      - [{s.get('id', '?')}] {s.get('claim', '')[:70]}")
    if final and not all_verified:
        fail("--final refused: not every source is verified. "
             "Run the editorial-review sub-agent first (see workflow/editorial-review.md).")

    is_draft = not all_verified
    suffix = "-DRAFT" if is_draft else ""

    # Logo (optional reversed-white PNG/SVG for the purple band) ------------ #
    logo = ""
    for name in ("logo.png", "logo.svg", "logo.jpg"):
        p = ASSETS / name
        if p.exists():
            logo = data_uri(p)
            break

    # Render ---------------------------------------------------------------- #
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    fonts_css = font_faces_css()
    core_css = fonts_css + (TEMPLATES / "styles_core.css").read_text()
    screen_css = core_css + "\n" + (TEMPLATES / "styles_screen.css").read_text()
    print_css = core_css + "\n" + (TEMPLATES / "styles_print.css").read_text()

    # Give each image page its own PDF page sized to the export's aspect (letter
    # width, proportional height) so the artwork is full-bleed with no bars.
    page_rules = []
    for p in pages:
        if p["kind"] == "image":
            n = p["index"] + 1
            page_rules.append(f"@page pimg{n} {{ size: 8.5in {8.5 / p['aspect']:.3f}in; margin: 0; }}")
            page_rules.append(f".page--image.page--{n} {{ page: pimg{n}; }}")
    if page_rules:
        print_css += "\n" + "\n".join(page_rules) + "\n"

    ctx = {
        "pages": pages,
        "logo": logo,
        "is_draft": is_draft,
        "verified": verified,
        "total": total,
        "build_date": _dt.date.today().isoformat(),
    }

    template = env.get_template("base.html.j2")
    out_dir = issue_dir / "output"
    out_dir.mkdir(exist_ok=True)

    # 1) Self-contained HTML (screen / email)
    html_doc = template.render(css=screen_css, for_pdf=False, **ctx)
    html_out = out_dir / f"newsletter-{issue_dir.name}{suffix}.html"
    html_out.write_text(html_doc, encoding="utf-8")
    print(f"  ✓ HTML  → {html_out.relative_to(ROOT)}")

    # 2) Print PDF (paged-media CSS) via WeasyPrint
    try:
        from weasyprint import HTML as WeasyHTML
    except Exception as e:  # pragma: no cover
        print(f"  ⚠ Skipping PDF — WeasyPrint unavailable ({e}).")
        return
    pdf_doc = template.render(css=print_css, for_pdf=True, **ctx)
    pdf_out = out_dir / f"newsletter-{issue_dir.name}{suffix}.pdf"
    WeasyHTML(string=pdf_doc, base_url=str(ROOT)).write_pdf(str(pdf_out))
    print(f"  ✓ PDF   → {pdf_out.relative_to(ROOT)}")

    if is_draft:
        print("\n  NOTE: Output is watermarked DRAFT because not all page-2 claims are verified.")
    else:
        print("\n  ✓ All claims verified — final output ready to distribute.")
    print()


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    final = "--final" in sys.argv
    issue_dir = resolve_issue(args[0] if args else None)
    build(issue_dir, final)


if __name__ == "__main__":
    main()
