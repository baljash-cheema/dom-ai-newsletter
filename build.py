#!/usr/bin/env python3
"""
DOM AI Newsletter — reproducible build pipeline.

Turns one plain-Markdown issue file into a precise, identical-format
HTML (email-ready, self-contained) and PDF (print-quality) every month.

Usage:
    .venv/bin/python build.py                 # builds the most recent issue
    .venv/bin/python build.py 2026-07         # builds issues/2026-07
    .venv/bin/python build.py issues/2026-07  # same thing
    .venv/bin/python build.py 2026-07 --final # refuses to build unless every
                                              #   source in sources.yaml is verified

Outputs land in <issue>/output/:
    newsletter-<issue>.html
    newsletter-<issue>.pdf
(or with a -DRAFT suffix + watermark if any claim is unverified)

Nothing in this script invents content. It only renders what is in
content.md and reports the verification state recorded in sources.yaml.
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
    "sane_lists",
    "smarty",       # typographic quotes / dashes
    "toc",
    "admonition",
]


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
            # accept "2026-07" or "issues/2026-07"
            cand = (ISSUES / arg) if not str(arg).startswith("issues") else (ROOT / arg)
        if not cand.exists():
            fail(f"Issue folder not found: {cand}")
        return cand
    # latest by folder name (YYYY-MM sorts correctly)
    candidates = sorted(p for p in ISSUES.iterdir() if p.is_dir() and (p / "content.md").exists())
    if not candidates:
        fail("No issues found. Create one by copying issue_template/ into issues/YYYY-MM/")
    return candidates[-1]


def data_uri(path: Path) -> str:
    """Inline a file as a base64 data URI so the HTML is fully self-contained."""
    mime, _ = mimetypes.guess_type(str(path))
    mime = mime or "application/octet-stream"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def load_sources(issue_dir: Path) -> list[dict]:
    sf = issue_dir / "sources.yaml"
    if not sf.exists():
        return []
    raw = yaml.safe_load(sf.read_text()) or {}
    return raw.get("sources", []) or []


def verification_state(sources: list[dict]) -> tuple[int, int, list[dict]]:
    """Return (verified_count, total, unverified_list)."""
    total = len(sources)
    unverified = [s for s in sources if not s.get("verified", False)]
    return total - len(unverified), total, unverified


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build(issue_dir: Path, final: bool) -> None:
    content_path = issue_dir / "content.md"
    if not content_path.exists():
        fail(f"No content.md in {issue_dir}")

    post = frontmatter.load(content_path)
    meta = post.metadata
    body_html = md.markdown(post.content, extensions=MD_EXTENSIONS, output_format="html5")

    # Verification gate ----------------------------------------------------- #
    sources = load_sources(issue_dir)
    verified, total, unverified = verification_state(sources)
    all_verified = total > 0 and not unverified

    print(f"\n  Issue:    {issue_dir.name}")
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

    # Logo (optional) ------------------------------------------------------- #
    logo = ""
    for name in ("logo.png", "logo.jpg", "logo.svg"):
        p = ASSETS / name
        if p.exists():
            logo = data_uri(p)
            break

    # Render ---------------------------------------------------------------- #
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    core_css = (TEMPLATES / "styles_core.css").read_text()
    screen_css = core_css + "\n" + (TEMPLATES / "styles_screen.css").read_text()
    print_css = core_css + "\n" + (TEMPLATES / "styles_print.css").read_text()

    ctx = {
        "meta": meta,
        "body": body_html,
        "logo": logo,
        "sources": sources,
        "is_draft": is_draft,
        "auto_references": meta.get("auto_references", True),
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
        print("\n  NOTE: Output is watermarked DRAFT because not all claims are verified.")
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
