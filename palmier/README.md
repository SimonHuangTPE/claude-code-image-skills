# Palmier AI Video Lab

把 Claude Code、Codex 或 Cursor 透過 MCP 接到 Palmier Pro，建立可視化、可二次修改的 AI 剪輯流程。

## 官方限制

- Apple Silicon Mac
- macOS 26 Tahoe
- Palmier Pro 開啟時提供 MCP：`http://127.0.0.1:19789/mcp`
- 編輯器與 MCP 可免費使用；生成式 AI 功能可能需要訂閱

## 安裝

1. 下載並安裝 Palmier Pro。
2. 開啟 Palmier Pro，建立空白專案。
3. 執行環境檢查：

```bash
bash palmier/scripts/check-environment.sh
```

4. 安裝 MCP：

```bash
# Claude Code
claude mcp add --transport http palmier-pro http://127.0.0.1:19789/mcp

# Codex
codex mcp add palmier-pro --url http://127.0.0.1:19789/mcp
```

5. 複製 Skills：

```bash
mkdir -p ~/.claude/skills
cp -R palmier/skills/palmier-video-edit ~/.claude/skills/
```

## 最小驗收流程

準備：

- `assets/talking-head.mp4`：30–90 秒口播
- `assets/broll/`：至少 3 段 B-roll
- `assets/logo.png`
- `assets/music.mp3`

對 Claude Code 或 Codex 下達：

> 使用 palmier-video-edit skill，依照 palmier/benchmark/acceptance-test.md 建立 60 秒直式短影音。先規劃，再透過 Palmier MCP 建立可編輯時間軸。不得只用 FFmpeg 直接輸出成片。完成後執行 QA 並回報分數。

## 標準工作流

1. Planner：分析素材、決定節奏與鏡頭。
2. Transcript：轉錄、切句、標示贅詞與停頓。
3. Timeline：建立主軌、B-roll、字幕、音樂與品牌軌。
4. Polish：調整音量、轉場、字幕安全區與節奏。
5. QA：依 benchmark 評分。
6. Human review：在 Palmier 時間軸人工修改。
7. Export：輸出 H.264 MP4，保留 Palmier 專案。

## 設計原則

- LOOP：每一階段都必須產出可檢查結果，再進入下一階段。
- HARNESS：用固定素材目錄、固定輸出規格、環境檢查與評分表限制 Agent。
- PROMPT：每次先建立 edit plan，再執行 MCP tool calls，最後驗證。
- Multi-Agent：Planner、Transcript、Timeline、Caption、Audio、QA 分工。
- Function Calling：所有時間軸修改必須映射為明確工具呼叫，不接受模糊的「幫我剪好」。
- Agent automation：重複任務以模板與 benchmark 驗證，不直接無限自動輸出。
