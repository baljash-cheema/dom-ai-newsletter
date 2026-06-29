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
cp issue_template/content.md "$DEST/content.md"
cp issue_template/sources.yaml "$DEST/sources.yaml"
echo "✓ Created $DEST"
echo "  1. Edit $DEST/content.md"
echo "  2. Record every claim in $DEST/sources.yaml"
echo "  3. Ask Claude to run the editorial-review pass"
echo "  4. ./build.sh $ISSUE"
