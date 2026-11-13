from pythonbpf import bpf, bpfglobal, section, map
from pythonbpf.maps import HashMap
from pythonbpf.helper import uid
from ctypes import c_void_p, c_uint32, c_uint64, c_int64


@bpf
@map
def Count() -> HashMap:
    return HashMap(key=c_uint32, value=c_uint64, max_entries=1024)


@bpf
@bpfglobal
def LICENSE() -> str:
    return "Dual BSD/GPL"


@bpf
@section("tracepoint/syscalls/sys_enter_execve")
def on_exec(ctx: c_void_p) -> c_int64:
    u_id = uid()
    count = Count.lookup(u_id)
    if count:
        Count.update(u_id, count + 1)
    else:
        Count.update(u_id, 1)
    return 0
