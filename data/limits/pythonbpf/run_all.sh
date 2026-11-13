#!/usr/bin/env bash
# Recompile every recorded Python-BPF limitation and log what happens.
# Compile only: compile_to_ir never loads or attaches, so this needs no kernel privileges.
set -uo pipefail
cd "$(dirname "$0")"
V=/root/experiment/.venv/bin/python
mkdir -p out
log="out/harness-$(date -u +%Y%m%dT%H%M%SZ).log"
: > "$log"

for p in l2_one_section l2_two_sections l4_subscript l4_atomic l3_struct_cast l3_local_buf; do
  echo "=== $p ===" | tee -a "$log"
  "$V" -c "from pythonbpf import compile_to_ir; compile_to_ir(filename='$p.py', output='out/$p.ll')" >>"$log" 2>&1
  echo "exit=$?" | tee -a "$log"
  if [ -f "out/$p.ll" ]; then
    echo "ir_lines=$(wc -l < "out/$p.ll")" | tee -a "$log"
  else
    echo "ir_lines=none" | tee -a "$log"
  fi
  # last meaningful stderr line, if any
  tail -n 3 "$log" | sed 's/^/    /'
done

echo "=== atomicrmw count ===" | tee -a "$log"
for f in out/l4_atomic.ll out/l4_subscript.ll; do
  [ -f "$f" ] && echo "$f: $(grep -c atomicrmw "$f")" | tee -a "$log"
done

echo "log: $log"
