from pythonbpf import bpf, bpfglobal, section
from ctypes import c_void_p, c_int64


@bpf
@bpfglobal
def LICENSE() -> str:
    return "Dual BSD/GPL"


@bpf
@section("tracepoint/syscalls/sys_enter_execve")
def on_exec(ctx: c_void_p) -> c_int64:
    print(f"arg0 = {ctx.args[0]}")
    return 0
