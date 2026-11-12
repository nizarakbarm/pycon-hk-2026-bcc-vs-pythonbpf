# Benchmark tree — what is here and what produced it

Everything in `data/raw/experiment/` comes from one host, one tracepoint, one trigger.

| item | value |
|---|---|
| host | `vmnono` (hostname `nono1`), 3 CPUs, openSUSE Leap 16.1, kernel 6.12.0-160100.7 |
| tracepoint | `syscalls/sys_enter_execve`, uid filter `uid == 1000` |
| trigger | `gen_exec N` (source in `trigger/`), run as user `operator` |
| frameworks | BCC (system `python3`) vs Python-BPF (`/root/experiment/.venv/bin/python3`) |
| arms | 2 frameworks × 3 callback variants (`count`, `A`, `B`) × N ∈ {20, 50, 100, 1000, 2000, 2000000} = 36 per pass |

```
experiment/
  with_map/           the six measured programs (bcc/ and pythonbpf/, identical structure,
                      only the callback body differs)
  scripts/            harness: the three sweeps, the per-arm runners, ranker, verifier
  trigger/            gen_exec.c + compiled binary; gen_unlink is a leftover from the
                      openat/unlink experiment, not part of these results
  timev_bench.sh      /usr/bin/time -v wrapper used for the RSS numbers
  results/README.md   pass-by-pass guide: formats, traps, regeneration commands
```

## What generated what

| pass | runner | output |
|---|---|---|
| 1 — unprofiled | `scripts/pass1_unprof_sweep.sh` → `scripts/rebenc_unprof.sh` | `results/unprofiled/*.log` — `[TIMING]` (process_time per phase) and `[RUSAGE]` (RSS, faults, context switches, user/sys split) |
| 2 — `strace -T` | `scripts/rebenc_straceT_sweep.sh` → `scripts/rebenc_straceT.sh` | `results/straceT/*.T.txt` (every syscall + duration), `.rank.txt` (via `scripts/rank_T.py`), `.prog.log` |
| 3 — `perf record` | `scripts/pass3_perfrec_sweep.sh` → `scripts/rebenc_perfrec.sh` | `results/perfrecord/*.{log,data,folded,svg}` — folded values are PMU cycles from `-F 199` frequency mode |

`scripts/rank_T.py` must regenerate `.rank.txt`; the harness's original inline ranker was
anchored on end-of-line and silently wrote empty files.

## The delivery gate — check this before trusting a number

Every arm must report `[SUMMARY] Events in map` equal to **N + 1**. The `+1` is the
trigger's own `exec`, not a lost or duplicated event. A shortfall means the burst fired
before the program attached (or the drain was too short) and the arm is invalid — the
harness prints `WARN`, and the two pre-gate failures are kept in `results/straceT/_failed/`.

The runner waits for `Starting poll` / `Starting to poll` in the program log before firing
the trigger. Do not replace that with a fixed sleep.

## Reproducing one arm

```bash
cd /root
env TAG=repro1 N=1000 VAR=count \
    OUT=/root/experiment/results/unprofiled T=0.5 \
    bash /root/experiment/scripts/rebenc_unprof.sh
```

Full sweeps, the perf/flamegraph regeneration and the interpretation rules are in
`results/README.md`.

## Where the raw logs live

`results/` is **not** in the git tree — it is 80 MB of text and data files. Download it from
the release asset `dataset-2026-10-13.tar.gz` and unpack at this level:

```bash
tar -xzf dataset-2026-10-13.tar.gz     # creates ./results/
```
