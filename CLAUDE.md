# CLAUDE.md — DOM AI Newsletter

## What this project is
A reproducible monthly newsletter for **all faculty** in the Department of
Medicine, produced by a subcommittee of the Education Committee. Purpose:
showcase what trainees are already doing with AI, upskill faculty, and teach
AI in clinical medicine / medical education. Audience is faculty physicians;
tone is credible, plain-language, and academically defensible.

**Non-negotiable: every factual claim is verified against a real source before
publication. No hallucinated facts, statistics, or citations — ever.** This is a
major academic medical center publishing under its own name.

## The four standing sections (every issue)
1. **Article of the Month** — plain-language summary of one paper Josh supplies,
   plus a clearly-labeled "Editor's Perspective" (opinion, boxed, separate from fact).
2. **Trainee Spotlight** — what a resident/fellow is doing with AI (Josh supplies;
   published only with permission; no PHI).
3. **AI Explainer** — one concept taught for busy faculty.
4. **News, Tools & Pitfalls** — verified roundup + tool tip + a safety/ethics caution.

## Sourcing model
Mix: **Josh supplies** the core article + trainee content; **Claude researches**
the news/tools/explainer sections (PubMed + web tools). Everything Claude adds is
source-verified before it ships.

## How to produce an issue
```bash
./new-issue.sh 2026-07        # 1. scaffold issues/2026-07 from the template
# 2. edit issues/2026-07/content.md  (plain Markdown, footnote every claim [^s1])
# 3. record every claim in issues/2026-07/sources.yaml
# 4. ask Claude: "Run the editorial review on issue 2026-07"
./build.sh 2026-07            # 5. draft build (watermarked until all verified)
./build.sh 2026-07 --final    # 6. final build — refuses unless ALL claims verified
```
Outputs: `issues/<issue>/output/newsletter-<issue>.{html,pdf}` (HTML is
self-contained/email-ready; PDF is print-quality US Letter).

## Anti-hallucination machinery (how it's enforced, not just promised)
- **`sources.yaml`** per issue: every claim → citation → resolvable id (DOI/PMID/URL)
  → `verified` flag. The build watermarks **DRAFT** until all are `verified: true`,
  and `--final` refuses to build otherwise. The gate is in code, not memory.
- **`workflow/editorial-review.md`**: the sub-agent process — Fact-Verifier (confirms
  each claim against the real source), Copy-Editor (clarity + fact/opinion separation),
  Red-Team (tries to refute the weakest claim). A claim survives only if verified AND
  not refuted. **Claude never flips `verified: true` without showing the evidence.**

## When acting as the editorial sub-agent
- Resolve every DOI/PMID/URL with the PubMed/web tools — never trust a remembered citation.
- Quote numbers/effect sizes/dates/populations from the source; do not paraphrase them.
- Label preprints/editorials/news as such; never present them as peer-reviewed evidence.
- If verification is ambiguous → cut the claim, don't hedge it.

## Toolchain / reproducibility notes
- Python 3.9 venv in `.venv/` (gitignored; recreate: `python3 -m venv .venv &&
  .venv/bin/pip install -r requirements.txt`). Deps pinned in `requirements.txt`.
- PDF rendering uses **WeasyPrint**, which needs Homebrew's pango/gobject/cairo.
  `build.py` auto-sets `DYLD_FALLBACK_LIBRARY_PATH` to the Homebrew lib dir and
  re-execs, so a plain run "just works" on this Mac. (`brew install pango` if ever missing.)
- Formatting is centralized: `templates/styles_core.css` (shared look),
  `styles_screen.css` (HTML/email), `styles_print.css` (PDF paged-media). Brand
  colors are CSS variables in `styles_core.css` `:root`.
- Generated outputs are **gitignored** — they are reproducible from source.

## Git / "save everything" (per global policy)
Josh does not run git. Claude commits after meaningful changes, pushes to GitHub,
and updates the memory file (`memory.md`). Never commit `.venv/`, outputs, raw data,
credentials, or unreleased/PHI-bearing trainee content.
