#!/usr/bin/env python3
"""Poll all kokovideo Kling jobs, download finished clips. Resumable."""
import json, os, subprocess, sys, time, urllib.request

ROOT = "/Users/jarvis/projects/kokovideo"
JOBS = "/tmp/kling_jobs.json"
STATE = f"{ROOT}/docs/kling_state.json"
OUTDIR = f"{ROOT}/video/clips"
os.makedirs(OUTDIR, exist_ok=True)


def q(gid):
    r = subprocess.run(["kling", "query_tasks", gid, "--skill-name", "kling-cli",
                        "--skill-version", "0.1.3", "--quiet"],
                       capture_output=True, text=True, timeout=180)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"ok": False, "parse_error": r.stdout[:300] + r.stderr[:300]}


def deep(o, keys):
    """find first value for any key name, case-insensitive"""
    out = {}
    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                lk = k.lower()
                if lk in keys and v not in out:
                    out[lk] = v
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(o)
    return out


def main():
    jobs = json.load(open(JOBS))
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    deadline = time.time() + 30 * 60
    while time.time() < deadline:
        pending = 0
        for shot in sorted(jobs):
            st = state.get(shot, {})
            if st.get("status") == "COMPLETED" and st.get("file"):
                continue
            gid = jobs[shot]["generationId"]
            d = q(gid)
            b = d.get("body", d)
            m = deep(b, {"status"})
            status = str(m.get("status", "?")).upper()
            urls = deep(b, {"url", "urlwithoutwatermark", "fileurl"})
            st = {"status": status, "gen": gid}
            if status in ("COMPLETED", "SUCCEED", "SUCCESS"):
                u = urls.get("urlwithoutwatermark") or urls.get("url") or urls.get("fileurl")
                st["url"] = u
                if u:
                    p = f"{OUTDIR}/{shot}.mp4"
                    try:
                        urllib.request.urlretrieve(u, p)
                        st["file"] = p
                        st["bytes"] = os.path.getsize(p)
                    except Exception as e:
                        st["dl_error"] = str(e)
            elif status in ("FAILED", "ERROR"):
                st["raw_error"] = json.dumps(b)[:400]
                pending += 1
            else:
                pending += 1
            state[shot] = st
            json.dump(state, open(STATE, "w"), indent=1)
            print(f"{shot}: {status}" + (f" -> {st.get('file')} ({st.get('bytes')}B)" if st.get("file") else ""), flush=True)
        if pending == 0:
            print("ALL DONE", flush=True)
            break
        print(f"...{pending} pending, sleeping 25s ({int(deadline - time.time())}s left)", flush=True)
        time.sleep(25)
    done = sum(1 for s in state.values() if s.get("file"))
    print(f"FINAL: {done}/9 clips downloaded", flush=True)


if __name__ == "__main__":
    main()
