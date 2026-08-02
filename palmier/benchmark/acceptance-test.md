# Palmier 60-Second Acceptance Test

## Goal

Measure whether an AI agent can turn raw assets into a usable first cut while preserving a visible, editable Palmier timeline.

## Input package

```text
assets/
  talking-head.mp4   # 30–90 seconds
  broll/
    01.mp4
    02.mp4
    03.mp4
  logo.png
  music.mp3
```

Recommended topic: a 45–60 second 4Wheels tire, wheel, maintenance, or recruitment short.

## Required output

- Editable Palmier project
- 1080x1920 H.264 MP4
- 45–60 second duration
- Dialogue, B-roll, captions, logo, music, and CTA on separate logical tracks
- QA report using the rubric below

## Test procedure

1. Open Palmier Pro and create a new project.
2. Run `bash palmier/scripts/check-environment.sh`.
3. Connect Claude Code or Codex to Palmier MCP.
4. Give the agent this instruction:

> Use the palmier-video-edit skill. Inspect all assets, create an edit plan, then build a 45–60 second 9:16 short in Palmier. Remove dead air and obvious failed takes, add at least three context-relevant B-roll placements, add Traditional Chinese captions using 4Wheels Standard, add logo and CTA, mix dialogue and music, preserve an editable timeline, run QA, revise critical defects, save and export.

5. Open the timeline and verify every claimed edit visually.
6. Change one caption and move one B-roll clip manually. The project must remain editable.
7. Export a second version without rebuilding the project.

## Scoring rubric — 100 points

| Area | Points | Pass criteria |
|---|---:|---|
| Timeline structure | 15 | Logical tracks, no unexplained gaps/offline media |
| Content selection and pacing | 15 | Removes dead air, coherent 45–60 second narrative |
| Caption accuracy and timing | 15 | Readable Traditional Chinese, phrase-level sync |
| Visual composition | 10 | 9:16 framing, safe areas respected |
| B-roll relevance | 10 | At least 3 useful placements, not random decoration |
| Audio quality | 15 | Clear speech, music ducking, fades, no clipping |
| Branding and CTA | 10 | Logo and clear final action present |
| Editability | 10 | Manual caption/clip change works without regeneration |

## Gate conditions

Automatic fail regardless of score:

- Only a flattened MP4 is produced
- Palmier timeline is missing or cannot be reopened
- Source media is overwritten
- Dialogue is inaudible or export is corrupt
- Agent reports completion without inspecting the timeline

## Maturity levels

- 90–100: production-ready first cut
- 80–89: usable with light manual correction
- 70–79: prototype; substantial correction needed
- Below 70: workflow not accepted

Target for initial rollout: at least 80 points on three consecutive runs using different source packages.

## Defect report format

```text
Score: __/100
Critical defects: __
Major defects: __
Minor defects: __
Manual correction time: __ minutes
Export path: __
Palmier project path: __
Recommended next change: __
```
