#!/usr/bin/env bash
# Content safety gate: fails (exit 1) if any pattern that must never ship
# appears in the repository content. Runs locally and in CI. Fail-closed:
# a hit on any pattern blocks the release until resolved.
set -uo pipefail
cd "$(dirname "$0")/.."

# Everything except VCS internals, build output, and this script itself
# (it necessarily contains the patterns it greps for).
SCAN_ARGS=(-rIEn --exclude-dir=.git --exclude-dir=dist --exclude-dir=node_modules \
  --exclude=publish-check.sh)

PATTERNS=(
  '[0-9]{11}'                                        # CPF-like 11-digit runs
  '\+55[0-9]{8,}'                                    # Brazilian phone numbers
  '[[:alnum:]._%+-]+@(gmail|hotmail|outlook|yahoo|uol|terra)\.'   # personal emails
  'sk-[A-Za-z0-9]{20,}'                              # API-key-like tokens
  'eyJ[A-Za-z0-9_-]{30,}\.'                          # JWT-like tokens
  'AKIA[0-9A-Z]{16}'                                 # AWS access keys
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'               # private key material
)

fail=0
for p in "${PATTERNS[@]}"; do
  hits="$(grep "${SCAN_ARGS[@]}" -- "$p" . 2>/dev/null || true)"
  if [ -n "$hits" ]; then
    echo "FAIL: pattern matched: $p"
    echo "$hits" | head -20
    fail=1
  fi
done

if [ "$fail" -ne 0 ]; then
  echo "publish-check: FAIL — resolve the hits above before publishing."
  exit 1
fi
echo "PASS: publish-check found no forbidden content."
