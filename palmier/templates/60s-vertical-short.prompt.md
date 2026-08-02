# 60-Second Vertical Short Prompt

Use the `palmier-video-edit` skill and Palmier MCP.

## Objective

Create a 45–60 second Traditional Chinese vertical short from the assets in `{{ASSET_DIRECTORY}}`.

## Brand and audience

- Brand: {{BRAND}}
- Topic: {{TOPIC}}
- Audience: {{AUDIENCE}}
- CTA: {{CTA}}

## Required process

1. Inspect every media asset and report duration, dimensions, audio presence, and likely role.
2. Write an edit decision list before changing the timeline.
3. Create a 1080x1920 sequence.
4. Build a 0–3 second hook, concise main section, and final CTA.
5. Remove dead air, failed takes, repeated phrases, and obvious filler while preserving natural speech.
6. Add at least three relevant B-roll placements.
7. Add Traditional Chinese phrase-level captions using 4Wheels Standard.
8. Put dialogue, music, captions, B-roll, logo, and CTA on logical separate tracks.
9. Duck music under speech, add short fades, and prevent clipping.
10. Inspect the completed timeline, fix critical defects, save the editable Palmier project, and export H.264 MP4.
11. Score the result using `palmier/benchmark/acceptance-test.md`.

## Hard constraints

- Do not replace Palmier timeline editing with a one-shot FFmpeg render.
- Do not overwrite source media.
- Do not claim completion without inspecting the final timeline.
- Report unresolved defects honestly.

## Completion report

Return:

- Project path
- Export path
- Duration and aspect ratio
- Timeline track summary
- Benchmark score
- Critical, major, and minor defects
- Estimated manual correction time
