from pythonbpf import bpf, bpfglobal, section
from pythonbpf.helper import probe_read
from ctypes import c_uint64, c_int64
from vmlinux import struct_pt_regs, struct_filename


@bpf
@bpfglobal
def LICENSE() -> str:
    return "Dual BSD/GPL"


@bpf
@section("kprobe/do_unlinkat")
def entry(ctx: struct_pt_regs) -> c_int64:
    fname = struct_filename(ctx.si)
    buf = c_uint64(0)
    probe_read(buf, 8, fname.name)
    print(f"name = {buf}")
    return 0
