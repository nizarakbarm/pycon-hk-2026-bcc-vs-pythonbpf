from pythonbpf import bpf, bpfglobal, section, struct
from pythonbpf.helper import probe_read_str
from ctypes import c_int64
from vmlinux import struct_pt_regs


@bpf
@struct
class buf_t:
    data: str(256)


@bpf
@bpfglobal
def LICENSE() -> str:
    return "Dual BSD/GPL"


@bpf
@section("kprobe/do_unlinkat")
def entry(ctx: struct_pt_regs) -> c_int64:
    ptr = ctx.si
    buf = buf_t()
    probe_read_str(buf.data, ptr)
    print(f"name = {buf.data}")
    return 0
