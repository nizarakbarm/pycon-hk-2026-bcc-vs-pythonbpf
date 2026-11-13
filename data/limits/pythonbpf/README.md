# Python-BPF limit repros — the talk's Part 4

Compile-only programs that reproduce each Python-BPF gap on slides **p28–p32** of the deck.
`pythonbpf.compile_to_ir` is used, so nothing is loaded or attached: no root, no kernel state, and
each check finishes in a second.

Measured 2026-11-13 on `vmnono`, kernel 6.12, pythonbpf **0.2.0**, pythonbpf repo at **f2e6fba**.

## Page map

| deck page | limit | file | expected |
|---|---|---|---|
| p28–p29 | enforcement: BCC removes the userspace hop, Python-BPF cannot deny | **not here** — needs `ghostlock/` and a live trigger; see this repo's `data/live-code/ghostlock/` | BCC trigger returns `rc = -9` from an in-kernel `bpf_send_signal`; Python-BPF reads `trace_pipe` and calls `os.kill` |
| p30 | two sections, same `struct_pt_regs` annotation → one shared `DILocalVariable` | `l2_two_sections.py` | `RecursionError` inside llvmlite `DIValue.__hash__` |
| p30 | control, one section | `l2_one_section.py` | compiles (exit 0) |
| p31 | cast `ctx.si` to `vmlinux.struct_filename` | `l3_struct_cast.py` | `ValueError: Struct type '<class 'vmlinux.struct_filename'>' not found` |
| p31 | local `@struct` buffer + `probe_read_str` | `l3_local_buf.py` | `ValueError: Expected pointer type, got i64` |
| p32 | `ctx.args[0]` | `l4_subscript.py`, `l4_subscript_expr.py` | `Variable 'arg0' not found in symbol table or vmlinux` / `NotImplementedError: Unsupported formatted value in f-string: 'ast.Subscript'` |
| p32 | `count + 1` is not atomic | `l4_atomic.py` | compiles; `grep -c atomicrmw` on the IR = **0** |
| p33 | `bpf_trace_printk` takes three varargs | **not here** — a kernel signature limit, not a Python-BPF gap | — |

`unlink_arg.py`, `unlink_arg_return.py` and `unlink_arg_return_bcc.py` are the original collected
programs that exposed the p31 gaps, kept as the historical record.

## Run

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install pythonbpf==0.2.0 llvmlite
# the repros import `from vmlinux import struct_pt_regs`; generate it from the running kernel's BTF
# in a checkout of github.com/pythonbpf/Python-BPF:
#   python3 tools/vmlinux-gen.py -o vmlinux.py
cp .../Python-BPF/vmlinux.py .

./run_all.sh          # compiles all six, writes out/*.ll and out/harness-<utc>.log
```

`run_all.sh` prints `exit=0` and a `.ll` for the controls, and `exit=1` plus the error line for each
gap. `vmlinux.py` is 7.6 MB and is generated per kernel, so it is not committed here.

## What the results mean

- `expr_pass.py` has **no `ast.Subscript` branch** — `grep -c Subscript pythonbpf/expr/expr_pass.py` = 0.
  The old note described the node falling through to `return None` silently; on 0.2.0 it fails loudly.
- There is **no `atomic_rmw`** anywhere in the package — `grep -rn atomic` finds only
  `DW_TAG_atomic_type`. `Count.update(k, count + 1)` therefore compiles to load → add → store.
- `send_signal`, `attach_lsm` and any `lsm` support are absent from the package, which is why p28's
  enforcement limit still stands.

Full analysis: `Atlas/Dots/Things/PythonBPF/Limitations/` in the speaker's vault, plus the
`Python-BPF` repository's own `tests/test_config.toml` xfail registry.
