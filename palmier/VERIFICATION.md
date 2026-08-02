# Delivery Verification

## Repository checks

- [x] Palmier module isolated from existing image skills
- [x] Claude Code and Codex MCP commands documented
- [x] Environment preflight script included
- [x] Standardized video editing skill included
- [x] Reusable 60-second prompt included
- [x] 100-point acceptance benchmark included
- [x] Editable-timeline gate included

## Local checks required on target Mac

These checks require the user's Apple Silicon Mac and cannot be executed from GitHub alone:

- [ ] macOS 26 Tahoe or newer
- [ ] Palmier Pro installed and opened
- [ ] `http://127.0.0.1:19789/mcp` responds
- [ ] Claude Code or Codex can list Palmier tools
- [ ] Test assets imported successfully
- [ ] AI creates and saves an editable timeline
- [ ] Manual caption and B-roll edit succeeds
- [ ] H.264 MP4 export succeeds
- [ ] Three separate benchmark runs score at least 80/100

## Acceptance command

```bash
bash palmier/scripts/check-environment.sh
```

Then run the prompt in:

```text
palmier/templates/60s-vertical-short.prompt.md
```

Score with:

```text
palmier/benchmark/acceptance-test.md
```
