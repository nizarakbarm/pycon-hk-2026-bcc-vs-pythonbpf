from pythonbpf import bpf, bpfglobal, section, BPF
from ctypes import c_void_p, c_char, c_int64, c_uint64
from pythonbpf.utils import trace_pipe
from vmlinux import struct_pt_regs

@bpf
@bpfglobal
def LICENSE() -> str:
    return "Dual BSD/GPL"

@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: struct_pt_regs) -> c_int64:
    dfd = ctx.di

    filename_ptr = ctx.si
    
    print(f"KPROBE ENTRY dfd = {dfd}, filename = {filename_ptr}")
    return 0

@bpf
@section("kretprobe/do_unlinkat")
def do_unlinkat_exit(ctx: struct_pt_regs) -> c_int64:
    ret = ctx.ax

    print(f"KPROBE EXIT ret = {ret}")
    return 0

b = BPF()
b.load()
b.attach_all()
trace_pipe()

