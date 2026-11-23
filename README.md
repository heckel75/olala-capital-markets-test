# Olala mini 7A1B: a one-hour capital-markets test

A small, reproducible test of **OVHcloud's Olala-v1.0-mini-7A1B** (open weights, Apache 2.0, released
17–19 November 2026) against two small open models, on one machine, with prompts from capital markets.

**What it is:** speed, memory, and six short tasks (three coding, two explanations, one grounded answer), with
automatic checks and a blind manual score.
**What it is not:** a benchmark. One machine, three samples per prompt, one scorer. Read §9 before quoting a
number.

---

## 1. Models

| Model | Type | File (8-bit GGUF) | Size | Source | sha256 |
|---|---|---|---|---|---|
| Olala mini 7A1B | MoE, ~1 B of 6.78 B parameters active per token; hybrid attention (Differential-TPA + Mamba-3); reasoning model | `Olala-v1.0-mini-7A1B-q8_0-safe2.gguf` | 6.88 GB | `OVHaiLLM/Olala-v1.0-mini-7A1B-GGUF` (official) | `0bb4560fa6800b41d16a15507ad1843ca17c0849ce0cc989bca337dcf55136d7` |
| Phi-4-mini (Instruct) | dense, 3.84 B | `microsoft_Phi-4-mini-instruct-Q8_0.gguf` | 4.08 GB | `bartowski/microsoft_Phi-4-mini-instruct-GGUF` (Microsoft publishes no GGUF for it) | `a12f242c4ee379b9da91673e5d78b30bfacfe4fd86a0b2259d2ecad5d93cb6c7` |
| Qwen3.5-9B (Instruct) | dense, 9.20 B | `Qwen_Qwen3.5-9B-Q8_0.gguf` | 9.80 GB | `bartowski/Qwen_Qwen3.5-9B-GGUF` | `b58fe056b5435070240de259f3f981aa38fee96825bbd78c088d5fd90e46f2b5` |

`q8_0-safe2` is OVH's own 8-bit variant (some tensors kept at higher precision). OVH publishes no 4-bit file: it
built one and withdrew it as measurably worse. 8-bit is therefore used for all three.

## 2. Machine and software (as tested, 20 November 2026)

| Item | Value |
|---|---|
| Machine | GEEKOM A9 Mega: AMD Ryzen AI Max+ 395 (16 cores / 32 threads, Zen 5), Radeon 8060S iGPU (gfx1151), 128 GB LPDDR5X-8000 unified memory, 96 GB available to the GPU |
| OS | Ubuntu Server 24.04, kernel `7.0.0-43-generic` |
| GPU stack | ROCm 7.2.1 (HIP 7.2.53211, Clang 22.0.0) |
| Runtime | **OVH's llama.cpp fork** `github.com/OVHai-LLM/llama.cpp`, commit **`55c22dca0c98`** (18 Nov 2026), ggml 0.25.3. Upstream llama.cpp, Ollama, LM Studio and Lemonade cannot load the `olala` architecture yet. All three models run through this same build |
| Python | 3.12 (runner: standard library only; checks: any Python with NumPy, in case a model uses it) |

OVH documents CUDA, Metal and CPU builds of the fork. **There is no documented AMD build.** The ROCm (HIP)
build below compiled and ran unchanged on this machine.

## 3. Setup from scratch

```bash
mkdir -p ~/dev/olala/models ~/dev/olala/results && cd ~/dev/olala
git clone https://github.com/OVHai-LLM/llama.cpp.git llama.cpp-olala
cd llama.cpp-olala && git checkout 55c22dca0c987f247c21b427c3b3a09e1a28187f

# CPU build (needs cmake, gcc/g++)
cmake -B build-cpu -DCMAKE_BUILD_TYPE=Release -DLLAMA_USE_PREBUILT_UI=OFF
cmake --build build-cpu -j 16

# AMD GPU build (ROCm installed; set GPU_TARGETS to your GPU)
HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
  cmake -S . -B build-hip -DGGML_HIP=ON -DGPU_TARGETS=gfx1151 -DCMAKE_BUILD_TYPE=Release -DLLAMA_USE_PREBUILT_UI=OFF
cmake --build build-hip -j 16
# NVIDIA: -DGGML_CUDA=ON instead; Mac: -DGGML_METAL=ON (see OVH's model card)

cd ~/dev/olala
hf download OVHaiLLM/Olala-v1.0-mini-7A1B-GGUF Olala-v1.0-mini-7A1B-q8_0-safe2.gguf --local-dir models
hf download bartowski/microsoft_Phi-4-mini-instruct-GGUF microsoft_Phi-4-mini-instruct-Q8_0.gguf --local-dir models
hf download bartowski/Qwen_Qwen3.5-9B-GGUF Qwen_Qwen3.5-9B-Q8_0.gguf --local-dir models
sha256sum models/*.gguf      # compare with §1
```

Put this package in `~/dev/olala/olala-test/`. Paths are set at the top of `run_test.py` (`BASE`, `FORK`,
`MODELS_DIR`).

## 4. Running the test (about one hour)

**0. Speed baseline (optional, ~5 min)**: the figures in §8.
```bash
cd ~/dev/olala/llama.cpp-olala
for m in Olala-v1.0-mini-7A1B-q8_0-safe2 microsoft_Phi-4-mini-instruct-Q8_0 Qwen_Qwen3.5-9B-Q8_0; do
  ./build-hip/bin/llama-bench -m ../models/$m.gguf -ngl 99 -fa 1 -p 512 -n 128 -r 3
  ./build-cpu/bin/llama-bench -m ../models/$m.gguf -t 16 -fa 1 -p 512 -n 128 -r 3 --repack 0
done
```

**1. Run the prompts (~20–30 min).** Nothing else should be using the GPU or memory bandwidth. The runner stops
if Ollama or Lemonade has a model loaded, or if port 8090 is busy.
```bash
cd ~/dev/olala/olala-test
python3 run_test.py                 # GPU build, 3 models x 6 prompts x 3 samples = 54 answers
```
For each model in turn it starts `llama-server` on **127.0.0.1:8090** (loopback only), waits until it is
ready, sends one warm-up request (not recorded), runs every prompt three times with seeds 1, 2, 3, reads GPU
memory before and after loading, then stops the server. Output goes to
`~/dev/olala/results/run_<date>_<time>_gpu/`: `raw.jsonl` (every answer, thinking and timing), `env.json`
(versions, commands, memory), `server_<model>.log`.
Options: `--backend cpu`, `--samples 1`, `--models olala-mini-7a1b`, `--prompts A B`, `--hash`.

**2. Automatic checks (~1–2 min)**
```bash
~/dev/ml-env/bin/python check_answers.py ~/dev/olala/results/run_<...>_gpu     # any Python with NumPy
```
→ `checks.md` (table + per-answer details) and `checks.jsonl`.

**3. Blind scoring (~15–20 min)**
```bash
python3 make_blind.py ~/dev/olala/results/run_<...>_gpu
```
Open `blind/scoring_packet.md`, fill `blind/scoring_sheet.csv` (18 answers: sample 1 of each model for each
prompt, shuffled, final answer only). **Do not open `blind/key.json` until you have finished.**

**4. Summary**
```bash
python3 summarize.py ~/dev/olala/results/run_<...>_gpu
```
→ `summary.md` and `summary.csv`: speed, memory, time to final answer, checks, blind scores.

## 5. What the automatic checks do

The code the models wrote **is executed** in a separate Python process, in a temporary folder, with a 30-second
limit, as your user. Only run this on answers from this test.

| Prompt | "correct" means | "complete" adds | Heuristic parts |
|---|---|---|---|
| A Sharpe | the function's value matches a defensible convention at 252 days **and** the same convention at 12 days (the parameter is really used) | type hints, docstring, ≥ 2 own tests found, default 252 (edge cases reported separately as `PASS_edges`) | own tests: functions named `test*` and `unittest` classes |
| B Bug | `[0.1, -0.1, 0.05]` → `[0.1, -0.01, 0.0395]` and `[]` → `[]` | explanation mentions compounding / multiplying | the explanation keyword search |
| C Portfolio | the printed value equals √Σ(wσ)² for the model's **own** portfolio; not the perfect-correlation value | stdlib only, 4 decimals, comment on correlation, weight-sum check, negative-weight check | the last three are text searches |
| D / E | (manual) | under 100 words, right language | word count covers the whole answer; language by common words |
| F Grounded | 17h35; stays in the book until validity ends; says the text gives no fees; no invented figure | ≤ 3 sentences, French | all text searches |

Reference answers and the traps each check targets: `reference.md`. A check can be wrong. Before quoting a cell,
read that answer's line in `checks.md`.

## 6. Manual scoring scale

Four criteria, 0–5, **5 is always best**:

- **correctness**: the finance and the code are right (use the automatic check, override with a reason in
  `notes`);
- **completeness**: every instruction followed;
- **clarity**: clear prose / readable code;
- **no_extra_content**: 5 = nothing invented, nothing unnecessary; lower for padding, off-topic material or
  claims not asked for (in F, anything beyond the text).

## 7. Settings, and why

| | Olala | Phi-4-mini | Qwen3.5-9B |
|---|---|---|---|
| Sampling | temp 0.8, top_p 0.9, top_k 40 (OVH's card; other samplers at the fork's defaults) | temp 0.0, greedy (Microsoft's examples): its three samples should be identical | temp 0.7, top_p 0.8, top_k 20, min_p 0, presence_penalty 1.5, repeat_penalty 1.0 (Qwen's card, non-thinking mode, general tasks) |
| Thinking | reasoning effort **low** (OVH's own CPU example) | none | **off** (`enable_thinking: false`) |
| Server flags | `-ngl 99 -fa 1 -nr -c 8192 -np 1 -t 16` for all three | same | same |

- **Each model runs at its maker's recommended settings.** One shared temperature would favour one model; low
  temperatures risk repetition loops in a reasoning model.
- **Only Olala thinks.** Its thinking costs time before the answer starts, which is why the summary reports
  **time to final answer** as well as tokens per second.
- **Every sampler is set explicitly for Phi and Qwen**, so llama.cpp's own defaults (e.g. min_p 0.05) do not
  leak in.
- **No repacking (`-nr`)**: OVH's advice for x86; on this CPU it made no measurable difference for any model.
- **GPU for the timed run**: every model is at its fastest there (§8).
- **Prompt changes from the original plan:** B no longer carries the `# <-- bug here` hint; F (grounded answer
  from a fictional text, in French) was added because it is the job Qwant uses Olala for.

## 8. Speed already measured (llama-bench, 8-bit, same fork build)

Tokens per second; generation = `tg128`, prompt = `pp512`.

| Model | CPU generation | GPU generation | GPU / CPU | CPU prompt | GPU prompt | Peak memory (CPU run) |
|---|---|---|---|---|---|---|
| Olala mini 7A1B | 61.5 | 63.6 | **1.03×** | ~700 | 1,209 | ~6.6 GiB |
| Phi-4-mini | 28.1 | 50.1 | 1.78× | ~357 | 2,878 | ~4.0 GiB |
| Qwen3.5-9B | 13.1 | 24.5 | 1.87× | ~133 | 1,179 | ~9.2 GiB |

- Olala is fully on the GPU (37/37 layers, 6.3 GiB in GPU memory), yet its generation is no faster than on the
  CPU, while both dense models gain ~1.8×. The cause was not measured; a likely one is that its new operations
  are not yet tuned for AMD GPUs.
- Memory follows the total parameters; speed follows the active ones, less than proportionally.
- OVH's own figures (160 tok/s on an NVIDIA RTX A4500, 50 tok/s on CPU) come from other hardware.

## 9. Limits

- One machine (an AMD integrated GPU, which OVH does not document), one run, three samples per prompt; Phi is
  greedy, so its three samples are one.
- Six prompts in one domain. They test a narrow job, not general ability.
- Only Olala reasons; that is by design (§7), and it is part of what is being measured.
- Automatic checks are partly text searches (§5). One person scores, blind but alone.
- Versions move: the fork, the models and the GPU stack were current on 20 November 2026.

## 10. Files

| File | What it does |
|---|---|
| `prompts.json` | the six prompts, exactly as sent |
| `run_test.py` | runs the models one at a time through `llama-server` on 127.0.0.1:8090 |
| `check_answers.py` | automatic checks (runs model-written code in a sandboxed subprocess with a timeout) |
| `make_blind.py` | shuffled, anonymised scoring packet and sheet |
| `summarize.py` | combines everything into `summary.md` |
| `reference.md` | expected answers and traps |

License of this package: MIT. Model licences: Olala Apache 2.0; Phi-4-mini MIT; Qwen3.5 Apache 2.0 (check each
model card).
