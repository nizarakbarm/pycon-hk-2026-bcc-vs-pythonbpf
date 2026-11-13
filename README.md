# Python eBPF — BCC C-String Runtime vs Python-BPF AST Ahead of Time

Talk for **PyCon HK 2026**, Software Engineering & Platforms track, Saturday 14 November 2026.

BCC compiles C at runtime. Python-BPF compiles Python ahead of time. This repo holds the deck
**and the measurements behind it**, so every number on a slide can be checked.

- Deck: https://nizarakbarm.github.io/pycon-hk-2026-bcc-vs-pythonbpf/ (`slides.html`)
- Dataset: [release `dataset-2026-10-13`](https://github.com/nizarakbarm/pycon-hk-2026-bcc-vs-pythonbpf/releases/tag/dataset-2026-10-13)
- My fork of the framework: [nizarakbarm/Python-BPF](https://github.com/nizarakbarm/Python-BPF)

## The four results

Same program, same tracepoint (`sys_enter_execve`), same trigger, two frameworks. N = 2,000,000
unless stated. Source: `data/raw/experiment/results/unprofiled`, `count` variant.

| | BCC | Python-BPF |
|---|---|---|
| startup CPU (one process, before the first event) | **0.4 s** (0.375–0.580 across runs) | **0.02 s** (0.020–0.027) |
| total CPU at 2M events | **134.568 s** | **103.658 s** |
| syscalls per event | **1.96** (3,913,286 / 2M) | **1.03** (2,055,624 / 2M) |
| peak RSS | **175 MB** | **22 MB** |

Startup is the big gap (16–21×). Per event the gap is 1.30×, and most of it is BCC's callback
path — 1,907,735 `gettid` calls, not framework overhead on both sides. Wall time is *not* used:
the trigger is fork-bound and varies 8–16% between runs.

## Layout

```
slides.html                     the deck — fixed 1280x720 canvas, no build step, no CDN
index.html                      redirect to slides.html
images/                         deck art
data/live-code/                 the programs on the code slides, including both GhostLock enforcers
data/limits/pythonbpf/          compile-only repros for the Part 4 gaps, one per slide p30–p32   (see its README)
data/raw/experiment/            host, scripts, trigger, programs   (see its README)
data/raw/experiment/results/    NOT in the tree — download the release asset
```

`data/raw/experiment/results/README.md` explains what each pass measured, the file formats,
the delivery gate and the traps (strace timings are unusable; perf CPU is comparable only
inside its own pass). Read it before quoting a number.

## Limit 1 in code — two enforcers, same probe

`data/live-code/ghostlock/` holds both halves of the enforcement demo. Both watch
`kprobe/do_futex`, tag the PI-futex op set (1 = `LOCK_PI`, 2 = `WAIT_REQUEUE_PI`,
3 = `CMP_REQUEUE_PI`) and act on the trigger, tag 3:

- `ghostlock_enforce_bcc.py` — calls `bpf_send_signal(SIGKILL)` inside the program. No
  userspace kill loop; measured on `vmnono` with BCC 0.36.0, the trigger returns `rc = -9`.
- `ghostlock_enforce.py` — Python-BPF has no deny helper, so the program `print`s a
  `GHOSTLOCK op=… tag=… pid=…` line, the process reads `/sys/kernel/tracing/trace_pipe` and
  calls `os.kill`. Pid reuse is handled by expiring handled entries for dead pids.

Neither denies the syscall: the signal is delivered after `do_futex` returns. The BCC file
carries a local `pt_regs_x64` layout because this kernel only forward-declares `pt_regs`.

## Reproduce one arm

```bash
# on the host, unpack the dataset asset first
tar -xzf dataset-2026-10-13.tar.gz            # creates ./results/
cd /root
env TAG=repro1 N=1000 VAR=count \
    OUT=/root/experiment/results/unprofiled T=0.5 \
    bash /root/experiment/scripts/rebenc_unprof.sh
```

Full sweeps — all 36 arms, all three passes — are in
`data/raw/experiment/results/README.md`. Arms must report `[SUMMARY] Events in map == N + 1`;
anything less is an invalid arm, not a fast one.

## Presenting the deck

`slides.html` works from `file://`, but Chrome's second-display fullscreen needs an http origin:

```bash
python3 -m http.server 8000     # or serve.py in the authoring repo
```

Then **Present on display** → allow window management → pick the projector.

Keys: arrows / space / PageUp / PageDown / Home / End, `O` overview, `P` presenter view,
`F` fullscreen, `S` speaker notes.
