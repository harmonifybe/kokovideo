# 2026-09-13 — kokovideo: 60s bilingual French colours lesson

**Commit:** `55b220e` (harmonifybe/kokovideo, main, public)
**Output:** `video/kokovideo_60s_720p.mp4` — 60.0s, 1280×720, h264, AAC 48 kHz stereo, 27 MB

## What was built
End-to-end kids' educational video from the supplied 3×3 storyboard (1280×720 sheet → 9 tiles, 427×240 each).

- **Frames:** `storyboard_frames/frame_01..09.png` (3×3 split). Upscaled copies for generation in `storyboard_frames_hd/` (1280×720, Lanczos).
- **Script:** `docs/shotlist.json` — bilingual narration (French colour word + English meaning), style lock, per-shot motion prompt, audio directive ("music and ambience only, no spoken words").
- **Narration:** `audio/narration/shot01..09.mp3`, edge-tts `en-US-AvaMultilingualNeural` (rate −5%), single voice across all 9 beats, 46.6 s total, longest line 5.86 s (fits 6.67 s slot).

## Generation
- Model: `kling-video-v3_0`, image-to-video, 720p, 7 s per clip, `enable_audio=true`, `prefer_multi_shots=false` (one continuous shot per beat).
- Inputs uploaded via `kling file_upload`; jobs submitted with `--task-trace-id kokovideo-shotNN`.
- **Cost: 63 credits/clip → 567 total** (9,980 → 9,413).
- Result: 9/9 COMPLETED, each 1280×720 @24 fps, 169 frames (7.042 s), AAC 44.1 kHz stereo.

## Assembly
- `build_video.py`: each clip trimmed to 160 frames @24 fps (6.6667 s) → **9 × 160 = 1440 frames = 60.0 s exact**; Kling ambience ducked to 0.35, narration delayed 0.35 s, `amix normalize=0` + `alimiter 0.95`.
- Verified: duration 60.021 s, video 1280×720 h264 @24, audio AAC 48 kHz 2ch.
- Audio check: master mean −19.7 dB / max −1.5 dB (no clipping); narration window mean −17.9 dB vs ambience-only −25.8 dB → narration audibly dominant.
- QC sheet of all 9 mid-clip frames: on-screen text intact ("Rouge / Rou-ge", "Quelle est cette couleur ?", "Bravo ! Tu connais les couleurs !"), character/style consistent, no warping or watermark.

## Pipeline notes / pitfalls
- `screencapture` at OS level fails on this box ("could not create image from display") — use `computer_use` for screenshots.
- git-lfs is **not installed** (only the filter config existed): mp4s are committed directly, so keep `video/_parts/` untracked to avoid bloat.
- `ffmpeg volumedetect` prints at info level — don't run it with `-v error` or you get no measurements.
