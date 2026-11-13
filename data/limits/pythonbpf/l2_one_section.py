from pythonbpf import bpf, bpfglobal, section
from ctypes import c_int64
from vmlinux import struct_pt_regs


@bpf
@bpfglobal
def LICENSE() -> str:
    return "Dual BSD/GPL"


@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: struct_pt_regs) -> c_int64:
    dfd = ctx.di
    print(f"ENTRY dfd = {dfd}")
    return 0
