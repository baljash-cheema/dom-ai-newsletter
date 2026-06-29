# AI in Clinical Medicine & Education — Monthly Newsletter

A reproducible monthly faculty newsletter from the Department of Medicine
Education Committee. One plain-Markdown file per issue builds into a clean,
identically-formatted **PDF** (print) and **HTML** (email) — with a built-in
verification gate so nothing ships unless every factual claim is confirmed
against a real source.

## Quick start

```bash
# one-time setup
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# each month
./new-issue.sh 2026-07     # create issues/2026-07 from the blank template
#   …edit issues/2026-07/content.md  (write in plain Markdown)
#   …list every factual claim in issues/2026-07/sources.yaml
#   …ask Claude: "Run the editorial review on issue 2026-07"
./build.sh 2026-07         # draft build (watermarked until all claims verified)
./build.sh 2026-07 --final # final build — only succeeds when 100% verified
```

Outputs land in `issues/2026-07/output/`.

## What's in each issue
**Article of the Month** · **Trainee Spotlight** · **AI Explainer** ·
**News, Tools & Pitfalls**

## How accuracy is guaranteed
Every claim is recorded in the issue's `sources.yaml` with a resolvable
identifier (DOI / PMID / URL). A sub-agent editorial review
(`workflow/editorial-review.md`) independently verifies each claim, copy-edits,
and red-teams the weakest assertions. The build **refuses to produce a final,
unwatermarked issue until every claim is verified** — the rule is enforced by
the tooling, not by trust.

## Layout
See `issues/0000-demo/` for a layout sample (sample text, not real claims).

## Repo map
| Path | What it is |
|------|------------|
| `build.py` / `build.sh` | the build pipeline (Markdown → HTML + PDF) |
| `new-issue.sh` | scaffolds a new month from the template |
| `issue_template/` | blank `content.md` + `sources.yaml` to copy each month |
| `templates/` | HTML layout + CSS (core / screen / print) |
| `workflow/editorial-review.md` | the verification process |
| `issues/<YYYY-MM>/` | one folder per published month |
| `CLAUDE.md` | full context for AI-assisted sessions |
| `memory.md` | running project memory across sessions |
