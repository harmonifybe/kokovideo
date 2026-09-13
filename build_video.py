#!/usr/bin/env python3
"""Assemble the 60s kokovideo master from 9 Kling clips + TTS narration.

Per shot: 160 frames @24fps (6.6667s) = 9 shots -> exactly 60.000s.
Video: 1280x720 h264 ; Audio: Kling ambience at 0.35 + narration delayed 0.35s.
"""
import json, os, subprocess, glob

ROOT = "/Users/jarvis/projects/kokovideo"
SHOTS = json.load(open(f"{ROOT}/docs/shotlist.json"))["shots"]
FPS = 24
FRAMES = 160           # 160/24 = 6.66667s  -> x9 = 60.000s
W, H = 1280, 720
AMB = 0.35             # kling ambience level
NAR_DELAY = 0.35
OUT = f"{ROOT}/video/kokovideo_60s_720p.mp4"
TMP = f"{ROOT}/video/_parts"
os.makedirs(TMP, exist_ok=True)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"FAILED: {' '.join(cmd[:8])}...\n{r.stderr[-1500:]}")
    return r


def probe(p):
    r = run(["ffprobe", "-v", "error", "-show_entries",
             "stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
             "-of", "json", p])
    return json.loads(r.stdout)["streams"]


def main():
    parts = []
    for s in SHOTS:
        clip = f"{ROOT}/video/clips/shot{s['id']:02d}.mp4"
        nar = f"{ROOT}/audio/narration/shot{s['id']:02d}.mp3"
        assert os.path.exists(clip), f"missing {clip}"
        assert os.path.exists(nar), f"missing {nar}"
        part = f"{TMP}/part{s['id']:02d}.mp4"
        dur = FRAMES / FPS
        fc = (
            f"[0:v]scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS}[v];"
            f"[0:a]aresample=48000,aformat=channel_layouts=stereo,volume={AMB}[amb];"
            f"[1:a]aresample=48000,adelay={int(NAR_DELAY*1000)}|{int(NAR_DELAY*1000)},"
            f"apad,atrim=0:{dur:.4f},pan=stereo|c0=c0|c1=c0[nar];"
            f"[amb][nar]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]"
        )
        run(["ffmpeg", "-y", "-v", "error",
             "-i", clip, "-i", nar,
             "-filter_complex", fc,
             "-map", "[v]", "-map", "[a]",
             "-frames:v", str(FRAMES), "-t", f"{dur:.4f}",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
             "-movflags", "+faststart", part])
        parts.append(part)
        print(f"part{s['id']:02d} ok  {dur:.3f}s", flush=True)

    lst = f"{TMP}/concat.txt"
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", "-movflags", "+faststart", OUT])
    st = probe(OUT)
    v = [x for x in st if x["codec_type"] == "video"][0]
    a = [x for x in st if x["codec_type"] == "audio"][0]
    d = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                   "-of", "csv=p=0", OUT]).stdout.strip())
    print(f"MASTER {OUT}")
    print(f"  duration={d:.3f}s  video={v['width']}x{v['height']} {v['codec_name']} @{v['r_frame_rate']}  "
          f"audio={a['codec_name']} {a['sample_rate']}Hz {a['channels']}ch  size={os.path.getsize(OUT)/1e6:.1f}MB")


if __name__ == "__main__":
    main()
