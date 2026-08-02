# Palmier MCP Integration

Palmier Pro must be running locally. Its HTTP MCP endpoint is:

```text
http://127.0.0.1:19789/mcp
```

## Claude Code

```bash
claude mcp add --transport http palmier-pro http://127.0.0.1:19789/mcp
claude mcp list
```

## Codex

```bash
codex mcp add palmier-pro --url http://127.0.0.1:19789/mcp
codex mcp list
```

## Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "palmier-pro": {
      "type": "http",
      "url": "http://127.0.0.1:19789/mcp"
    }
  }
}
```

## Recommended supporting tools

Supporting tools are optional and must not replace Palmier timeline operations:

- Filesystem access for controlled asset folders
- FFmpeg for probing, transcoding, loudness analysis, and final validation
- Speech-to-text for transcript drafts
- Git for versioning prompts, skills, templates, and plugins

Do not expose Palmier's local MCP endpoint to the public internet. Keep it bound to localhost.

## Connection smoke test

1. Open Palmier Pro.
2. Open or create a project.
3. Confirm the client lists `palmier-pro`.
4. Ask the agent to inspect the active Palmier project and list available timeline/media operations.
5. Do not begin the benchmark until read operations succeed.

## Failure handling

- Connection refused: Palmier is closed or the MCP server is not active.
- Tool list empty: restart Palmier and the AI client.
- Changes not visible: ensure the correct project/sequence is selected, then inspect before retrying.
- Repeated destructive edits: restore the project copy and run the skill in PLAN-only mode first.
