# Contributing & adapting

Thanks for your interest! This repo is the build pipeline behind the Northwestern
Department of Medicine *AI in Medical Education* newsletter. It's MIT-licensed —
you're welcome to **fork it, adapt it for your own department or program, or
suggest improvements**.

## Want to run your own newsletter from this?

1. Fork the repo, then follow the **Quick start** in the [README](README.md).
2. Each issue is one plain-Markdown file (`content.md`) plus a verification
   ledger (`sources.yaml`) — no page-layout work required.
3. Make it yours:
   - Brand colors live as CSS variables in `templates/styles_core.css` (`:root`).
   - Masthead/title/editors are in each issue's Markdown frontmatter.
   - `./new-issue.sh YYYY-MM` scaffolds a fresh month from `issue_template/`.

## The one rule we don't bend: every claim is verified

The build **refuses to produce a final, unwatermarked issue until every factual
claim in `sources.yaml` is marked `verified: true`** with a resolvable identifier
(DOI / PMID / URL). The sub-agent process is described in
[`workflow/editorial-review.md`](workflow/editorial-review.md). If you adapt this,
please keep that gate — anti-hallucination by construction is the whole point.

No protected health information (PHI) belongs in any issue, ever.

## Proposing a change

- **Found a bug or have an idea?** Open an issue.
- **Sending a PR?** Keep it focused. If it touches the build, note how you tested
  it — e.g., `./build.sh 0000-demo` should still produce clean HTML + PDF.

## Questions / want help adapting it

Open a GitHub issue. If you're setting this up for your own training program and
want a hand, just say so in the issue — happy to help.
