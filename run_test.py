#!/usr/bin/env python3
"""Olala test runner for the A9 Mega.

Starts llama-server from the Olala llama.cpp fork for one model at a time (loopback only, port 8090),
sends every prompt in prompts.json SAMPLES times, measures timings from the stream, records memory,
then stops the server and moves to the next model. Standard library only.

Usage:
    python3 run_test.py                  # GPU build (build-hip), all models, 3 samples
    python3 run_test.py --backend cpu    # CPU build (build-cpu)
    python3 run_test.py --models olala-mini-7a1b --samples 1 --prompts A   # quick check
"""
import argparse
import datetime
import hashlib
import json
import os
import platform
import re
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

HOME = os.path.expanduser("~")
BASE = os.path.join(HOME, "dev", "olala")
FORK = os.path.join(BASE, "llama.cpp-olala")
MODELS_DIR = os.path.join(BASE, "models")
RESULTS_DIR = os.path.join(BASE, "results")
HERE = os.path.dirname(os.path.abspath(__file__))
HOST, PORT = "127.0.0.1", 8090      # 8080 is Watchlog's on this box: never use it here
CTX = 8192
THREADS = 16                        # physical cores of the Ryzen AI Max+ 395

# Sampling: each model at its own model card's recommended settings (runbook D5/D6).
# Phi-4-mini and Qwen3.5-9B: every sampler set explicitly so llama.cpp defaults do not leak in.
# Olala: exactly OVH's command (temp/top_p/top_k), other samplers at the fork's defaults.
MODELS = [
    {
        "name": "olala-mini-7a1b",
        "file": "Olala-v1.0-mini-7A1B-q8_0-safe2.gguf",
        "sampling": {"temperature": 0.8, "top_p": 0.9, "top_k": 40},
        "extra": {"reasoning_effort": "low"},
    },
    {
        "name": "phi-4-mini",
        "file": "microsoft_Phi-4-mini-instruct-Q8_0.gguf",
        "sampling": {"temperature": 0.0, "top_p": 1.0, "top_k": 0, "min_p": 0.0,
                     "presence_penalty": 0.0, "repeat_penalty": 1.0},
        "extra": {},
    },
    {
        "name": "qwen3.5-9b",
        "file": "Qwen_Qwen3.5-9B-Q8_0.gguf",
        "sampling": {"temperature": 0.7, "top_p": 0.8, "top_k": 20, "min_p": 0.0,
                     "presence_penalty": 1.5, "repeat_penalty": 1.0},
        "extra": {"chat_template_kwargs": {"enable_thinking": False}},
    },
]


def sh(cmd, timeout=60):
    """Run a command, return (exit code, combined output). Never raises."""
    try:
        p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:  # missing command, timeout
        return -1, f"{e.__class__.__name__}: {e}"


def gtt_used_bytes():
    code, out = sh(["rocm-smi", "--showmeminfo", "gtt"])
    m = re.search(r"GTT Total Used Memory \(B\):\s*(\d+)", out)
    return int(m.group(1)) if m else None


def port_in_use(host, port):
    with socket.socket() as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0


def preflight(force):
    problems = []
    if port_in_use(HOST, PORT):
        problems.append(f"port {PORT} is already in use on {HOST}")
    code, out = sh(["ollama", "ps"])
    if code == 0 and len([l for l in out.strip().splitlines() if l.strip()]) > 1:
        problems.append("Ollama has a model loaded (run: ollama stop <model>)")
    code, out = sh(["lemonade-server", "status"])
    if code == 0 and "No models loaded" not in out:
        problems.append("Lemonade has a model loaded (run: lemonade-server unload)")
    if problems:
        print("Preflight found problems:\n  - " + "\n  - ".join(problems))
        if not force:
            sys.exit("Stopped. Fix the above, or rerun with --force.")
    else:
        print("Preflight OK: port free, Ollama and Lemonade idle.")


def wait_health(proc, timeout=300):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if proc.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(f"http://{HOST}:{PORT}/health", timeout=5) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False


def vm_hwm_kb(pid):
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1])
    except Exception:
        return None
    return None


def split_think(content, reasoning):
    """If a template put the thinking inside the content as <think>...</think>, move it to reasoning."""
    if reasoning or "<think>" not in content:
        return content, reasoning
    m = re.search(r"<think>(.*?)</think>", content, re.S)
    if not m:
        return content, reasoning
    return (content[:m.start()] + content[m.end():]).strip(), m.group(1).strip()


def chat(text, model, seed, max_tokens):
    body = {
        "messages": [{"role": "user", "content": text}],
        "stream": True,
        "stream_options": {"include_usage": True},
        "max_tokens": max_tokens,
        "seed": seed,
    }
    body.update(model["sampling"])
    body.update(model["extra"])
    req = urllib.request.Request(
        f"http://{HOST}:{PORT}/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    rec = {"t_first_token_s": None, "t_first_answer_s": None, "finish_reason": None,
           "usage": None, "timings": None, "n_content_chunks": 0, "n_reasoning_chunks": 0, "error": None}
    content, reasoning = [], []
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=1800) as resp:
            for raw in resp:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if obj.get("usage"):
                    rec["usage"] = obj["usage"]
                if obj.get("timings"):
                    rec["timings"] = obj["timings"]
                for ch in obj.get("choices") or []:
                    d = ch.get("delta") or {}
                    now = time.perf_counter() - t0
                    rc, c = d.get("reasoning_content"), d.get("content")
                    if rc:
                        reasoning.append(rc)
                        rec["n_reasoning_chunks"] += 1
                        if rec["t_first_token_s"] is None:
                            rec["t_first_token_s"] = now
                    if c:
                        content.append(c)
                        rec["n_content_chunks"] += 1
                        if rec["t_first_token_s"] is None:
                            rec["t_first_token_s"] = now
                        if rec["t_first_answer_s"] is None:
                            rec["t_first_answer_s"] = now
                    if ch.get("finish_reason"):
                        rec["finish_reason"] = ch["finish_reason"]
    except urllib.error.HTTPError as e:
        rec["error"] = f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:500]}"
    except Exception as e:
        rec["error"] = f"{e.__class__.__name__}: {e}"
    rec["t_total_s"] = time.perf_counter() - t0
    rec["content"], rec["reasoning"] = split_think("".join(content), "".join(reasoning))
    return rec


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["gpu", "cpu"], default="gpu")
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--models", nargs="*", help="subset of model names")
    ap.add_argument("--prompts", nargs="*", help="subset of prompt ids, e.g. A B")
    ap.add_argument("--hash", action="store_true", help="also compute sha256 of the model files (slow)")
    ap.add_argument("--force", action="store_true", help="run even if preflight finds problems")
    args = ap.parse_args()

    build = "build-hip" if args.backend == "gpu" else "build-cpu"
    server_bin = os.path.join(FORK, build, "bin", "llama-server")
    if not os.path.exists(server_bin):
        sys.exit(f"Not found: {server_bin}")

    with open(os.path.join(HERE, "prompts.json")) as f:
        prompts = json.load(f)
    if args.prompts:
        prompts = [p for p in prompts if p["id"] in args.prompts]
    models = [m for m in MODELS if not args.models or m["name"] in args.models]
    for m in models:
        m["path"] = os.path.join(MODELS_DIR, m["file"])
        if not os.path.exists(m["path"]):
            sys.exit(f"Model file not found: {m['path']}")

    preflight(args.force)

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    run_dir = os.path.join(RESULTS_DIR, f"run_{stamp}_{args.backend}")
    os.makedirs(run_dir, exist_ok=True)
    raw_path = os.path.join(run_dir, "raw.jsonl")

    env = {
        "started": datetime.datetime.now().isoformat(timespec="seconds"),
        "host": platform.node(),
        "kernel": platform.release(),
        "python": sys.version.split()[0],
        "backend": args.backend,
        "server_bin": server_bin,
        "fork_commit": (lambda r: r[1].strip() if r[0] == 0 else "unknown")(sh(["git", "-C", FORK, "rev-parse", "HEAD"])),
        "hip_version": (lambda r: r[1].strip() if r[0] == 0 else "unknown")(sh(["hipconfig", "--version"])),
        "samples": args.samples,
        "ctx": CTX,
        "threads": THREADS,
        "port": PORT,
        "prompts": [p["id"] for p in prompts],
        "models": [],
    }

    total = len(models) * len(prompts) * args.samples
    done = 0
    for m in models:
        cmd = [server_bin, "-m", m["path"], "-t", str(THREADS), "-fa", "1", "-nr",
               "-c", str(CTX), "-np", "1", "--host", HOST, "--port", str(PORT),
               "-ngl", "99" if args.backend == "gpu" else "0"]
        info = {"name": m["name"], "file": m["file"], "bytes": os.path.getsize(m["path"]),
                "sampling": m["sampling"], "extra": m["extra"], "server_cmd": cmd}
        if args.hash:
            print(f"Hashing {m['file']} ...")
            info["sha256"] = sha256(m["path"])
        info["gtt_before_bytes"] = gtt_used_bytes()
        log_path = os.path.join(run_dir, f"server_{m['name']}.log")
        print(f"\n=== {m['name']}: starting llama-server ({args.backend})")
        t_load = time.time()
        with open(log_path, "w") as log:
            proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            if not wait_health(proc):
                info["error"] = f"server did not become healthy; see {log_path}"
                print(info["error"])
                env["models"].append(info)
                continue
            info["load_s"] = round(time.time() - t_load, 1)
            warm = chat("Bonjour", m, seed=0, max_tokens=16)       # warm-up, not recorded
            info["warmup_error"] = warm["error"]
            info["gtt_loaded_bytes"] = gtt_used_bytes()
            for p in prompts:
                for s in range(1, args.samples + 1):
                    done += 1
                    print(f"[{done}/{total}] {m['name']} prompt {p['id']} sample {s} ...", end=" ", flush=True)
                    rec = chat(p["text"], m, seed=s, max_tokens=p.get("max_tokens", 4096))
                    rec.update({"model": m["name"], "prompt": p["id"], "sample": s, "seed": s,
                                "backend": args.backend})
                    with open(raw_path, "a") as f:
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    tps = (rec.get("timings") or {}).get("predicted_per_second")
                    print(f"{rec['t_total_s']:.1f} s"
                          + (f", {tps:.1f} tok/s" if tps else "")
                          + (f", finish={rec['finish_reason']}" if rec["finish_reason"] != "stop" else "")
                          + (f", ERROR {rec['error']}" if rec["error"] else ""))
            info["gtt_peak_after_bytes"] = gtt_used_bytes()
            info["server_vm_hwm_kb"] = vm_hwm_kb(proc.pid)
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
            env["models"].append(info)
            time.sleep(3)

    env["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
    with open(os.path.join(run_dir, "env.json"), "w") as f:
        json.dump(env, f, indent=2)
    print(f"\nDone. Results in {run_dir}")
    print(f"Next: ~/dev/ml-env/bin/python {os.path.join(HERE, 'check_answers.py')} {run_dir}")


if __name__ == "__main__":
    main()
