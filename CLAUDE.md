# CLAUDE.md — DOM Education Newsletter

## What this project is
A reproducible **monthly, two-page newsletter** for the Northwestern Department
of Medicine, produced by the Education Committee. One repo generates the entire
newsletter as a combined **PDF** (print) and **HTML** (email):

- **Page 1 — DOM Education Committee.** Welcome, the year's topics, and the
  standing sections (Upcoming Events, Policies & Updates, Resources, Highlights),
  plus a feedback/QR block. Audience: educators, program leaders, coordinators,
  trainees.
- **Page 2 — AI in Medical Education.** One worthwhile paper on AI in clinical
  medicine / medical education, summarized plainly and **verified**, plus a boxed
  Editor's Perspective. Audience: faculty physicians. Tone: credible,
  plain-language, academically defensible.

Both pages share one visual identity (deep-purple masthead + footer bands, the
Northwestern Medicine lockup, condensed headline type). Page 2 is the recurring
"second page" the committee promised on the inaugural page 1.

**Non-negotiable (page 2): every factual claim is verified against a real source
before publication. No hallucinated facts, statistics, or citations — ever.**
This is a major academic medical center publishing under its own name.

## Issue structure (files)
```
issues/<YYYY-MM>/
  issue.yaml    # shared masthead metadata: month, volume, editors, disclaimer
  page1.md      # committee content (front matter: title)
  page2.md      # AI Article of the Month (front matter: title)
  sources.yaml  # verification ledger for PAGE 2's claims
  output/       # generated PDF + HTML (gitignored)
```
`issue.yaml` is merged **under** each page's own front matter, so month/volume/
editors live in one place. `issues/2026-06/` is the full worked example.

## How to produce an issue
```bash
./new-issue.sh 2026-08        # scaffold issues/2026-08 from issue_template/
# 1. set month/volume in issues/2026-08/issue.yaml
# 2. edit issues/2026-08/page1.md   (committee content; fill [PLACEHOLDER]s)
# 3. edit issues/2026-08/page2.md   (AI article) + record every claim in sources.yaml
# 4. ask Claude: "Run the editorial review on issue 2026-08"   (page 2)
./build.sh 2026-08            # draft build (watermarked until all claims verified)
./build.sh 2026-08 --final    # final — refuses unless ALL page-2 claims verified
```
Outputs: `issues/<issue>/output/newsletter-<issue>.{html,pdf}` — one file, two
pages. HTML is self-contained/email-ready; PDF is print-quality US Letter.

## Page 2 — AI in Medical Education (the one paper)
**One page, one paper.** A single **Article of the Month** — a plain-language
summary of one paper Josh supplies, plus a clearly-labeled boxed **Editor's
Perspective** (opinion, separate from fact). That is the whole page. Resist scope
creep — no news roundup, no tool tips, no second paper. If it overflows, **cut
the copy** — do not shrink the house scale for one issue.

Three sections were cut on 2026-07-22 (Trainee Spotlight, AI Explainer, and
Evidence/Tools & Pitfalls). They live in git history — do not reintroduce them
without Josh explicitly asking.

**Josh supplies the paper.** Claude writes the plain-language summary and drafts
the Editor's Perspective by reading the actual source (PubMed + web tools) —
never a remembered version. Everything is source-verified before it ships.

## Page 1 — DOM Education Committee (clean, brand-matched)
A code-native layout in the same brand (chosen 2026-07-28 over a pixel-faithful
Canva recreation). Standing structure: **Welcome**, a "Who we are" committee note
(the Committee's mix of PCs/PDs/DAs + a roster link), the year's **topic grid**
(inaugural issue), the **In Every Issue** cards (Upcoming Events, Policies &
Updates, Resources, Highlights), and a **feedback + QR** block.

Page-1 details Josh still owes are marked `[PLACEHOLDER: …]` and render in red so
they're impossible to miss: committee roster link, his signature, his email, the
feedback QR, and event dates. **Do not invent institutional facts** — leave the
placeholder until Josh provides the real value.

## House format & templates
- **`templates/base.html.j2`** — document shell; loops over the pages.
- **`templates/page.html.j2`** — one page = masthead band + content + optional
  colophon (page 2 only) + footer band.
- **CSS** (concatenated in `build.py`): `styles_core.css` (shared look + brand
  vars in `:root`), `styles_screen.css` (HTML/email), `styles_print.css` (PDF
  paged-media, full-bleed bands). Change brand colors once in `:root`.

**What stays identical every issue (so it reads as one publication):** the
masthead bands (NM lockup, condensed title, `issue_label · Vol · No · Month`,
book emblem), the footer band (CONNECT | COLLABORATE | EDUCATE | EMPOWER ·
nm.org/medicine/education), the page-2 colophon (editor roster + disclaimer), and
the section-header style. The masthead/footer come from `page.html.j2` +
`issue.yaml`, so keeping those constant keeps them constant.

Editor roster (page-2 colophon), same names/order every issue: Yvonne Lee,
Stefanie Reiff, Mac Walter, Josh Cheema, Katie Hufmeyer, Aashish Didwania. Update
in `issue_template/issue.yaml` (and the current issue) if membership changes.

## Visual components
Defined in `styles_core.css`. Markdown-inside-HTML is enabled (`md_in_html`).
**⚠️ Footnote markers (`[^1]`) do NOT render inside raw HTML blocks** — keep them
in the paragraph before/after a component.

Page 2 (use about **two** per issue — the page is small):
- `!!! note "Editor's Perspective — from the subcommittee"` → opinion box.
- `!!! horizon "On the horizon"` → next-topic teaser (e.g., adaptive learning).
- `!!! caution "…"` → red caution box.
- `<div class="scene">…</div>` → an "adapted from Figure N" scene (see 2026-06
  page2.md — an original adaptation of a figure, **never a reproduced image**).
- `<div class="statcard"><div class="stat-num">…</div><div class="stat-text">…</div></div>` → big-number callout.
- `<div class="cardrow"><div class="card">…</div>…</div>` → 2–3 side-by-side cards.
- `<span class="landmark-tag">…</span>` + `<a class="read-link" href="…">Read the full article</a>` in a `<div class="article-meta">` → the citation-header row.

Page 1: `.welcome-script` (Great Vibes wordmark), `.committee-note`, `.signature`
(Dancing Script), `.topics-panel` + `.topic` tiles, `.feature-cards` / `.fcard`
with `.fcard-badge` (circular icon) + `.fcard-foot` (colored pill), and
`.feedback` + `.feedback-icon` + `.qr-box`. **Icons are inline SVGs** with
`stroke="currentColor"`, so a tile/card's `color` drives icon + accent stripe +
heading together; the topic tiles rotate through six brand colors via
`:nth-child`. Copy shapes from `issues/2026-06/page1.md`.

## Anti-hallucination machinery (page 2)
- **`sources.yaml`** per issue: every claim → citation → resolvable id
  (DOI/PMID/URL) → `verified` flag. The build watermarks **DRAFT** until all are
  `verified: true`; `--final` refuses otherwise. The gate is in code, not memory.
- **`workflow/editorial-review.md`**: the sub-agent process — Fact-Verifier,
  Copy-Editor, Red-Team. A claim survives only if verified AND not refuted.
  **Claude never flips `verified: true` without showing the evidence.**

When acting as the editorial sub-agent:
- Resolve every DOI/PMID/URL with the PubMed/web tools — never a remembered citation.
- Quote numbers/effect sizes/dates/populations from the source; don't paraphrase them.
- Label preprints/editorials/news as such; never present them as peer-reviewed evidence.
- If verification is ambiguous → cut the claim, don't hedge it.

## Toolchain / reproducibility
- Python 3.9 venv in `.venv/` (gitignored; recreate: `python3 -m venv .venv &&
  .venv/bin/pip install -r requirements.txt`). Deps pinned in `requirements.txt`.
- PDF rendering uses **WeasyPrint** (Homebrew pango/gobject/cairo). `build.py`
  auto-sets `DYLD_FALLBACK_LIBRARY_PATH` and re-execs, so a plain run just works.
- **WeasyPrint quirk:** flexbox `gap` and `position:fixed`/`absolute` are
  unreliable in this version — a sized flex item and a text item can overlap, and
  absolutely-positioned children may not paint. Use **inline-block or
  `display:table`** for side-by-side lockups/badges (see `.nm-mark`, `.topic`),
  and normal block flow for the full-bleed bands. The logo, topic badges, and
  section headers were all reworked to avoid these.
- **Script fonts** (`assets/fonts/*.woff2` — Great Vibes + Dancing Script, OFL;
  see `assets/fonts/README.md`) are subset to woff2 and inlined into the CSS by
  `build.py`. `Brotli` (pinned in requirements) lets WeasyPrint decode woff2.
- Optional `assets/logo.png` (reversed-white) replaces the built-in CSS lockup.
- Generated outputs are gitignored — reproducible from source.

## Git / "save everything"
Josh does not run git. Claude commits after meaningful changes, pushes to GitHub,
and updates the memory file (`memory.md`, which is **gitignored / local-only**).
Never commit `.venv/`, outputs, raw data, credentials, or PHI.
