# Editorial Review & Verification Workflow

This is the process that lets the Department stand behind every word. It runs
**before** an issue is built `--final`. The goal: **zero unverified claims, zero
hallucinated citations.**

## Roles (sub-agents)

The monthly review uses independent sub-agents so no single pass is trusted blindly:

1. **Fact-Verifier** — for each entry in `sources.yaml`, independently confirms the
   `claim` is actually supported by the cited source. Uses the PubMed and web
   tools to pull the real abstract/paper/page. Checks:
   - Does the source exist? (resolve the DOI / PMID / URL — no fabricated IDs)
   - Does it actually say what the claim says? (no overstatement, right direction
     of effect, correct numbers, correct population)
   - Is the citation formatted correctly and pointing to the right item?
   Sets `verified: true` and writes the supporting quote/location into `notes`,
   or leaves it `false` with an explanation.

2. **Copy-Editor** — reads `content.md` for clarity, tone (faculty audience),
   accuracy of plain-language explanations, and that **opinion is visibly
   separated from fact** (Editor's Perspective boxes). Flags any sentence making a
   factual claim that has *no* footnote pointing to `sources.yaml`.

3. **Red-Team / Skeptic** — actively tries to find the weakest claim and refute
   it. Assumes something is wrong and looks for it: outdated stat, tool that
   doesn't do what we said, a "study shows" that's really a preprint or an
   editorial. Anything it can't defend gets cut or softened.

A claim survives only if the Fact-Verifier confirms it **and** the Red-Team
cannot refute it.

## The standing rules

- **No claim without a source.** Every factual sentence maps to a `sources.yaml` id.
- **No source without a resolvable identifier.** A real DOI, PMID, or live URL.
  If it can't be resolved, it does not ship.
- **Numbers are quoted, not paraphrased.** Effect sizes, percentages, dates, and
  populations are copied from the source, not remembered.
- **Preprints, editorials, and news are labeled as such** — never dressed up as
  peer-reviewed evidence.
- **Opinion is boxed and labeled** ("Editor's Perspective"). Never blended into
  the neutral summary.
- **Uncertain → cut.** When verification is ambiguous, the claim is removed, not
  hedged. The newsletter would rather say less than say something wrong.
- **Trainee content** is published only with the trainee's permission and contains
  no PHI.

## How to run it (what to tell Claude)

> "Run the editorial review on issue 2026-07."

Claude will: spawn the Fact-Verifier across every `sources.yaml` entry (resolving
each DOI/PMID/URL with the PubMed and web tools), then the Copy-Editor and
Red-Team passes, then report a table of every claim with its verdict and the
supporting quote. Claude updates `sources.yaml` (`verified`, `verified_by`,
`notes`) and edits `content.md` for anything that failed. **Claude does not flip a
claim to verified without showing you the evidence.**

## The build gate

`build.py` reads `sources.yaml`:
- Any `verified: false` → output is watermarked **DRAFT** and filenames get a
  `-DRAFT` suffix.
- `./build.sh <issue> --final` **refuses to build** unless every claim is verified.

So the only way to produce a clean, distributable PDF/HTML is to have passed
verification. The process is enforced by the tooling, not by memory.
