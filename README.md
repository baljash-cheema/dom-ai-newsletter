# DOM Education Newsletter

A reproducible monthly newsletter from the Northwestern Department of Medicine
Education Committee. Each issue builds from plain-Markdown source into one clean,
identically-formatted **two-page** document — **PDF** (print) and **HTML**
(email) — with a built-in verification gate so nothing ships unless every
factual claim on the AI page is confirmed against a real source.

**Page 1** — DOM Education Committee content (welcome, topics, events, policies,
resources, highlights, feedback).
**Page 2** — *AI in Medical Education*: one plain-language, source-verified
Article of the Month plus a boxed Editor's Perspective.

## Quick start

```bash
# one-time setup
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# each month
./new-issue.sh 2026-08     # scaffold issues/2026-08 from the blank template
#   …set the month/volume in issues/2026-08/issue.yaml
#   …edit issues/2026-08/page1.md   (committee content)
#   …edit issues/2026-08/page2.md   (AI Article of the Month)
#   …list every page-2 claim in issues/2026-08/sources.yaml
#   …ask Claude: "Run the editorial review on issue 2026-08"
./build.sh 2026-08         # draft build (watermarked until all claims verified)
./build.sh 2026-08 --final # final build — only succeeds when 100% verified
```

Outputs land in `issues/2026-08/output/`.

## How accuracy is guaranteed
Every page-2 claim is recorded in the issue's `sources.yaml` with a resolvable
identifier (DOI / PMID / URL). A sub-agent editorial review
(`workflow/editorial-review.md`) independently verifies each claim, copy-edits,
and red-teams the weakest assertions. The build **refuses to produce a final,
unwatermarked issue until every claim is verified** — the rule is enforced by
the tooling, not by trust.

## Repo map
| Path | What it is |
|------|------------|
| `build.py` / `build.sh` | the build pipeline (Markdown → combined HTML + PDF) |
| `new-issue.sh` | scaffolds a new month from the template |
| `issue_template/` | blank `issue.yaml` + `page1.md` + `page2.md` + `sources.yaml` to copy each month |
| `templates/` | HTML layout (`base` + `page`) + CSS (core / screen / print) |
| `workflow/editorial-review.md` | the page-2 verification process |
| `issues/<YYYY-MM>/` | one folder per issue — see `issues/2026-06/` for a full worked example |
| `assets/` | embedded script fonts (`fonts/`, OFL) + optional `logo.png` (reversed-white) for the masthead band |
| `CLAUDE.md` | full context for AI-assisted sessions |

## Built with, and licensed

This newsletter and its build pipeline were created with
[Claude Code](https://claude.com/claude-code). The code is open-source under the
[MIT License](LICENSE) — free for anyone to use, adapt, or run for their own
newsletter. The bundled script fonts (`assets/fonts/`, Great Vibes & Dancing
Script) keep their own [SIL Open Font License 1.1](assets/fonts/OFL.txt).
Questions or want a hand adapting it? Open an issue or reach out.
