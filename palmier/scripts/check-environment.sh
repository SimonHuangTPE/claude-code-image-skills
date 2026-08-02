#!/usr/bin/env bash
set -euo pipefail

fail=0

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "FAIL: Palmier Pro currently requires macOS."
  fail=1
else
  echo "PASS: macOS detected."
fi

arch="$(uname -m)"
if [[ "$arch" != "arm64" ]]; then
  echo "FAIL: Apple Silicon arm64 required; detected $arch."
  fail=1
else
  echo "PASS: Apple Silicon detected."
fi

major="$(sw_vers -productVersion 2>/dev/null | cut -d. -f1 || echo 0)"
if [[ "$major" -lt 26 ]]; then
  echo "FAIL: macOS 26 Tahoe or newer required; detected $(sw_vers -productVersion 2>/dev/null || echo unknown)."
  fail=1
else
  echo "PASS: macOS version is supported."
fi

for cmd in curl ffmpeg; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "PASS: $cmd available."
  else
    echo "WARN: $cmd is missing. Install with Homebrew if the workflow needs it."
  fi
done

if curl -fsS --max-time 2 http://127.0.0.1:19789/mcp >/dev/null 2>&1; then
  echo "PASS: Palmier MCP endpoint responded."
else
  echo "WARN: Palmier MCP did not respond. Open Palmier Pro and retry."
fi

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi

echo "Environment is eligible for Palmier Pro testing."
