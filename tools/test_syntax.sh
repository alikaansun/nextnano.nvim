#!/usr/bin/env bash
# Checks that sample.in highlights the way the syntax file promises, and that
# omni completion is scoped to the enclosing group. Exits non-zero on any miss.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"

nvim --clean --headless -u NONE \
  --cmd "set rtp^=$repo" \
  -c "set nomore" \
  -S "$repo/tools/test_syntax.vim" \
  "$repo/sample.in"
