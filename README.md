# kokovideo

Storyboard source for the Koko colors-in-French video (0–40s).

## Contents

- `storyboard.png` — original 3x3 storyboard sheet (1280x720)
- `storyboard_frames/` — the sheet split into 9 individual frames (3x3, 424x240-ish each)
  - `frame_01_r1c1.png` — 0-4s · Bonjour! (intro)
  - `frame_02_r1c2.png` — 4-8s · Rouge
  - `frame_03_r1c3.png` — 8-12s · Jaune
  - `frame_04_r2c1.png` — 12-16s · Vert
  - `frame_05_r2c2.png` — 16-20s · Bleu
  - `frame_06_r2c3.png` — 20-24s · Violet
  - `frame_07_r3c1.png` — 24-28s · Orange
  - `frame_08_r3c2.png` — 28-34s · Question (Quelle est cette couleur?)
  - `frame_09_r3c3.png` — 34-40s · Bravo! (outro)

## Splitting

`split_grid.py` — PIL-based 3x3 crop. Grid boundaries are rounded so all
9 tiles come out at 426–427 x 240 px from a 1280x720 source.
