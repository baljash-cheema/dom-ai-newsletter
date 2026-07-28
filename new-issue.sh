#!/usr/bin/env bash
# Start a new monthly issue by copying the blank template.
#   ./new-issue.sh 2026-07
set -euo pipefail
cd "$(dirname "$0")"
ISSUE="${1:-}"
if [ -z "$ISSUE" ]; then
  echo "Usage: ./new-issue.sh YYYY-MM   (e.g. ./new-issue.sh 2026-07)" >&2
  exit 1
fi
DEST="issues/$ISSUE"
if [ -e "$DEST" ]; then
  echo "✗ $DEST already exists — not overwriting." >&2
  exit 1
fi
mkdir -p "$DEST"
cp issue_template/issue.yaml   "$DEST/issue.yaml"
cp issue_template/page1.md     "$DEST/page1.md"
cp issue_template/page2.md     "$DEST/page2.md"
cp issue_template/sources.yaml "$DEST/sources.yaml"
echo "✓ Created $DEST"
echo "  1. Set the month/volume in $DEST/issue.yaml"
echo "  2. Edit $DEST/page1.md  (committee content)"
echo "  3. Edit $DEST/page2.md  (AI Article of the Month) + record every claim in sources.yaml"
echo "  4. Ask Claude to run the editorial-review pass on page 2"
echo "  5. ./build.sh $ISSUE     (then ./build.sh $ISSUE --final once verified)"
