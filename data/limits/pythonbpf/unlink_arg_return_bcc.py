#!/usr/bin/env python3
# BCC variant of unlink_arg_return.py.
#
# Same program: two sections, kprobe/do_unlinkat and kretprobe/do_unlinkat.
# Same fields, same registers:
#   entry: dfd = ctx.di (rdi), filename = ctx.si (rsi)
#   exit : ret        = ctx.ax (rax)
#
# BCC compiles both functions in ONE program and one compilation unit. This is
# safe here: BCC emits no llvmlite debug metadata, so the shared-DILocalVariable
# RecursionError from the Python-BPF variant cannot occur.
from bcc import BPF

program = r"""
#include <uapi/linux/ptrace.h>

int do_unlinkat_entry(struct pt_regs *ctx) {
    int dfd = (int)PT_REGS_PARM1(ctx);          // 1st arg, rdi = ctx.di
    u64 filename = (u64)PT_REGS_PARM2(ctx);     // 2nd arg, rsi = ctx.si, struct filename *
    bpf_trace_printk("KPROBE ENTRY dfd = %d, filename = %lld\n",
                     dfd, (long long)filename);
    return 0;
}

int do_unlinkat_exit(struct pt_regs *ctx) {
    long ret = (long)PT_REGS_RC(ctx);           // return value, rax = ctx.ax
    bpf_trace_printk("KPROBE EXIT ret = %ld\n", ret);
    return 0;
}
"""

b = BPF(text=program)
b.attach_kprobe(event="do_unlinkat", fn_name="do_unlinkat_entry")
b.attach_kretprobe(event="do_unlinkat", fn_name="do_unlinkat_exit")
print("attached: kprobe/do_unlinkat + kretprobe/do_unlinkat", flush=True)

while True:
    try:
        (_, _, _, _, _, line) = b.trace_fields()
        print(line.decode("utf-8", "replace").strip(), flush=True)
    except KeyboardInterrupt:
        break
