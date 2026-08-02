# Palmier Video Edit Skill

## Trigger

Use when the user asks to edit, cut, caption, polish, assemble, or export a video through Palmier Pro.

## Mandatory behavior

1. Confirm the Palmier MCP server is reachable.
2. Inventory source media before editing.
3. Produce an edit plan with target duration, aspect ratio, hook, sections, B-roll, caption style, audio plan, CTA, and export settings.
4. Use Palmier MCP timeline operations. Do not substitute a one-shot FFmpeg render unless the user explicitly requests a flattened render.
5. Preserve a fully editable Palmier project.
6. Run the acceptance rubric before claiming completion.

## Default short-video specification

- Canvas: 1080x1920, 9:16
- Frame rate: follow primary source, otherwise 30 fps
- Duration: 45–60 seconds
- Hook: first 0–3 seconds
- Main content: 3–48 seconds
- CTA: final 5–8 seconds
- Caption safe area: avoid top 10% and bottom 18%
- Dialogue target: around -14 LUFS integrated
- Music: duck under speech; no clipping
- Export: H.264 MP4, high quality

## Agent loop

### 1. PLAN
Return a structured edit plan before invoking tools.

### 2. BUILD
Create tracks in this order:

- V1 primary talking head
- V2 B-roll and product images
- V3 titles, captions, logo, CTA
- A1 dialogue
- A2 music
- A3 sound effects

### 3. INSPECT
Check gaps, overlaps, offline media, unreadable captions, abrupt audio, duplicated clips, missing CTA, and duration.

### 4. REVISE
Fix all critical failures. Repeat inspection once.

### 5. REPORT
Return project location, export location, duration, aspect ratio, completed actions, unresolved issues, and benchmark score.

## Function-calling contract

Every tool action must be narrow and observable. Prefer actions equivalent to:

- inspect project/timeline/media
- import media
- create or select sequence
- add track
- insert clip at time
- trim clip
- split clip
- move clip
- set volume or fade
- add caption/title
- apply transition/effect
- save project
- export sequence

Never request an unbounded action such as “make it viral” without converting it into measurable edits.

## Caption preset: 4Wheels Standard

- Traditional Chinese
- Maximum two lines
- 10–16 Chinese characters per line where practical
- Bold white glyphs
- Strong dark outline or shadow
- Important product names and numbers highlighted
- Avoid decorative emoji unless requested
- Time captions to natural phrases, not every word

## Multi-agent roles

- Planner Agent: edit decision list
- Transcript Agent: transcription, cleanup, phrase segmentation
- Timeline Agent: assembly and pacing
- Caption Agent: subtitle timing and styling
- Audio Agent: speech clarity, ducking, fades
- QA Agent: rubric scoring and defect list

One orchestrator owns final decisions and prevents agents from editing the same timeline range concurrently.
