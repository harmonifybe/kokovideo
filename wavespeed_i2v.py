#!/usr/bin/env python3
"""kokovideo / MiniMax H3 run: 9 frame -> 10s clips at 480p via the wavespeed API.

Same workflow as the Kling run, only the video backend changes:
  storyboard_frames_hd/frame_NN.png (published on raw.githubusercontent, 1280x720 = 16:9)
      -> wavespeed-ai/minimax-h3/image-to-video   (French prompt, resolution 480p, duration 10)
      -> video/clips_h3/shotNN.mp4

Usage:  python3 wavespeed_i2v.py [submit|poll|all]
"""
import json, os, subprocess, sys, time, urllib.request

ROOT = "/Users/jarvis/projects/kokovideo"
SLUG = "wavespeed-ai/minimax-h3/image-to-video"
RES = "480p"
DUR = 10
FPS = 24
RAW = "https://raw.githubusercontent.com/harmonifybe/kokovideo/main"
CLIPS = f"{ROOT}/video/clips_h3"
PAYLOADS = f"{ROOT}/docs/h3_payloads"
STATE = f"{ROOT}/docs/h3_state.json"
SHOTS = json.load(open(f"{ROOT}/docs/shotlist_fr.json"))
os.makedirs(CLIPS, exist_ok=True)
os.makedirs(PAYLOADS, exist_ok=True)


def cli(*args, timeout=180):
    r = subprocess.run(["wavespeed", *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise SystemExit(f"wavespeed {' '.join(args[:3])} failed:\n{r.stdout[-800:]}\n{r.stderr[-800:]}")
    return json.loads(r.stdout)


def unwrap(body):
    return body["data"] if isinstance(body, dict) and "data" in body else body


def load_state():
    return json.load(open(STATE)) if os.path.exists(STATE) else {}


def save_state(st):
    json.dump(st, open(STATE, "w"), indent=1, sort_keys=True)


def build_payloads():
    keys = []
    for s in SHOTS["shots"]:
        payload = {
            "prompt": f"{SHOTS['style_lock']}\n\n{s['prompt']}\n\n{SHOTS['negative_fr']}",
            "image": f"{RAW}/{s['frame']}",
            "resolution": RES,
            "duration": DUR,
            "seed": -1,
        }
        p = f"{PAYLOADS}/shot{s['id']:02d}.json"
        json.dump(payload, open(p, "w"), ensure_ascii=False, indent=1)
        keys.append(s["id"])
    print(f"payloads written: {len(keys)} -> {PAYLOADS}  (res={RES} dur={DUR}s, AR from 16:9 input image)")
    return keys


def submit():
    st = load_state()
    for s in SHOTS["shots"]:
        key = f"shot{s['id']:02d}"
        if st.get(key, {}).get("id"):
            print(f"{key}: already submitted {st[key]['id']}")
            continue
        body = unwrap(cli("run", SLUG, "--file", f"{PAYLOADS}/{key}.json"))
        st[key] = {"id": body["id"], "status": body.get("status", "created"),
                   "url": body.get("urls", {}).get("get", "")}
        save_state(st)
        print(f"{key}: submitted id={body['id']} status={body.get('status')}", flush=True)
        time.sleep(0.6)


def poll():
    st = load_state()
    deadline = time.time() + 3600
    while time.time() < deadline:
        pending = [k for k, v in st.items() if v.get("status") not in ("completed", "failed")]
        if not pending:
            break
        for key in sorted(pending):
            body = unwrap(cli("status", st[key]["id"]))
            st[key]["status"] = body.get("status")
            if body.get("status") == "completed":
                st[key]["output"] = body.get("outputs", [""])[0]
                st[key]["inference_ms"] = body.get("timings", {}).get("inference")
            if body.get("status") == "failed":
                st[key]["error"] = body.get("error", "unknown")
            save_state(st)
            print(f"  {key}: {st[key]['status']}", flush=True)
        if all(v.get("status") in ("completed", "failed") for v in st.values()):
            break
        time.sleep(10)
    save_state(st)
    return st


def download():
    st = load_state()
    for key in sorted(st):
        v = st[key]
        if v.get("status") != "completed":
            print(f"{key}: {v.get('status')} — skipped ({v.get('error','')})")
            continue
        dest = f"{CLIPS}/{key}.mp4"
        if not os.path.exists(dest) or os.path.getsize(dest) < 10000:
            req = urllib.request.Request(v["output"], headers={"User-Agent": "curl/8"})
            with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
                f.write(r.read())
        v["file"] = dest
        v["bytes"] = os.path.getsize(dest)
        save_state(st)
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames,sample_rate,channels",
                                "-of", "json", dest], capture_output=True, text=True).stdout
        v["probe"] = json.loads(probe)["streams"]
        print(f"{key}: {v['bytes']/1e6:.2f}MB {[(s.get('codec_type'), s.get('width'), s.get('height'), s.get('nb_frames'), s.get('r_frame_rate')) for s in v['probe']]}")
    save_state(st)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what == "reset":
        ids = [int(x) for x in sys.argv[2:]]
        st = load_state()
        for i in ids:
            key = f"shot{i:02d}"
            st.pop(key, None)
            f = f"{CLIPS}/{key}.mp4"
            if os.path.exists(f):
                os.remove(f)
        save_state(st)
        print(f"reset shots {ids} — state + clips cleared")
    if what in ("submit", "all"):
        build_payloads()
        submit()
    if what in ("poll", "all"):
        poll()
    if what in ("all", "download"):
        download()
