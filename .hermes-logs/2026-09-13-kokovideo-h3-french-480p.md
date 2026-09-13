# kokovideo — rerun via wavespeed API (MiniMax H3) — 2026-09-13

**Commit:** a75344d — "Rerun kokovideo via wavespeed-ai/minimax-h3/image-to-video: 9x10s 480p 16:9, French prompts + French narration"

## What was built
Same 9-shot storyboard workflow as the Kling run, video backend swapped to `wavespeed-ai/minimax-h3/image-to-video` through the `wavespeed` CLI (wavespeed API).

- Shots: 9 × 10s = **90.021s** master (240 frames @24fps per shot = exactly 10.000s each)
- **854x480 (16:9)** h264, AAC 48kHz stereo, 25.4 MB → `video/kokovideo_90s_480p.mp4`
- Params sent: `resolution=480p`, `duration=10`, `seed=-1`, `image` = raw.githubusercontent.com/harmonifybe/kokovideo/main/storyboard_frames_hd/... (repo public, so no base64 needed; the CLI rejects `--image-url`)
- Prompts and audio direction **French only**; narration = edge-tts `fr-FR-VivienneMultilingualNeural`, rate -5%
- The model has no aspect-ratio parameter: AR follows the first-frame image throughput (720p). Pipeline crops native 832x480 to exact 16:9 (832x468) then scales to 854x480 — no padding bars.

## Pipeline results
- Inference: 9/9 `completed`, 51.7–84.3s each (median ~60s), billed ≈ $0.40/shot (~$7.20 total incl. one regeneration pass).
- Audio mix: H3 native ambience at 0.30 + narration delayed 0.40s → mean -20.7 dB, max -2.3 dB (no clipping).
- Visual QC: 2x 3x3 sheets (t=2s, t=8s per shot).

## Known source-level artefacts (not model errors)
The input storyboard tiles already carry burned-in timecode badges ("20-24s", "24-28s", "28-34s", "34-40s") and a speaker/volume icon (shots 05/06/07). H3 animates them rather than removing them, so they persist in the master — exactly as in the Kling version. Removing them requires cleaning the source PNGs (inpaint badge + icon) and regenerating; the model cannot be prompted out of inherited text.

## New files
- `docs/shotlist_fr.json` — French prompts (no bracketed timecodes → "D'abord/Ensuite"), French narration, `negative_fr` block, resolution/duration/AR spec
- `wavespeed_i2v.py` — `submit | poll | download | reset <ids>` (parallel-safe, state in `docs/h3_state.json`)
- `build_video_h3.py` — crop-to-16:9 + scale, ambience/narration mix, concat to master
- `audio/narration_fr/` — 9 French TTS lines; `video/clips_h3/` — 9 clips (pass1 archived in `video/clips_h3_pass1/`)
