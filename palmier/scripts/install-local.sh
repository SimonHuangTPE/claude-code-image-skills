#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILL_SRC="$ROOT_DIR/palmier/skills/palmier-video-edit"
SKILL_DST="$HOME/.claude/skills/palmier-video-edit"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "ERROR: Palmier Pro currently requires macOS."
  exit 1
fi

if [[ "$(uname -m)" != "arm64" ]]; then
  echo "ERROR: Apple Silicon arm64 is required."
  exit 1
fi

mkdir -p "$HOME/.claude/skills"
rm -rf "$SKILL_DST"
cp -R "$SKILL_SRC" "$SKILL_DST"
echo "Installed Claude skill: $SKILL_DST"

if command -v claude >/dev/null 2>&1; then
  if ! claude mcp list 2>/dev/null | grep -q "palmier-pro"; then
    claude mcp add --transport http palmier-pro http://127.0.0.1:19789/mcp
  fi
  echo "Claude MCP configured."
else
  echo "WARN: Claude Code CLI not found; skipped Claude MCP registration."
fi

if command -v codex >/dev/null 2>&1; then
  if ! codex mcp list 2>/dev/null | grep -q "palmier-pro"; then
    codex mcp add palmier-pro --url http://127.0.0.1:19789/mcp
  fi
  echo "Codex MCP configured."
else
  echo "WARN: Codex CLI not found; skipped Codex MCP registration."
fi

bash "$ROOT_DIR/palmier/scripts/check-environment.sh"

echo "Local Palmier integration installed. Open Palmier Pro before running the benchmark."
