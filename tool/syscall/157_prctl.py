import os

output_dir = "./tool/cfiles/157_prctl"
os.makedirs(output_dir, exist_ok=True)

prctl_options = {
    "PR_SET_PDEATHSIG": ["SIGINT", "SIGKILL"],
    "PR_GET_PDEATHSIG": ["NULL"],
    "PR_GET_DUMPABLE": ["NULL"],
    "PR_SET_DUMPABLE": ["SUID_DUMP_USER", "SUID_DUMP_ROOT"],
    "PR_GET_UNALIGN": ["NULL"],
    "PR_SET_UNALIGN": ["PR_UNALIGN_NOPRINT", "PR_UNALIGN_SIGBUS"],
    "PR_SET_FPEMU" : ["PR_FPEMU_NOPRINT","PR_FPEMU_SIGFPE"],
    "PR_GET_FPEMU": ["NULL"],
    "PR_PR_SET_FPEXC" : ["PR_FP_EXC_SW_ENABLE", "PR_FP_EXC_DIV", "PR_FP_EXC_OVF", "PR_FP_EXC_UND", "PR_FP_EXC_RES", "PR_FP_EXC_INV", "PR_FP_EXC_DISABLED", "PR_FP_EXC_NONRECOV", "PR_FP_EXC_ASYNC", "PR_FP_EXC_PRECISE"],
    "PR_PR_GET_FPEXC": ["NULL"],
    "PR_SET_NAME": ["\"test_name\""],
    "PR_GET_NAME": ["NULL"],
    "PR_SET_SECCOMP": ["SECCOMP_MODE_DISABLED", "SECCOMP_MODE_STRICT", "SECCOMP_MODE_FILTER"],
    "PR_GET_SECCOMP": ["NULL"],
    "PR_GET_ENDIAN": ["NULL"],
    "PR_SET_ENDIAN": ["PR_ENDIAN_BIG", "PR_ENDIAN_LITTLE", "PR_ENDIAN_PPC_LITTLE"],
    "PR_GET_TSC": ["NULL"],
    "PR_SET_TSC": ["PR_TSC_ENABLE", "PR_TSC_SIGSEGV"],
    "PR_GET_SECUREBITS": ["NULL"],
    "PR_SET_SECUREBITS": ["SECBIT_NOROOT", "SECBIT_NOROOT_LOCKED", "SECBIT_NO_SETUID_FIXUP", "SECBIT_NO_SETUID_FIXUP_LOCKED", "SECBIT_KEEP_CAPS", "SECBIT_KEEP_CAPS_LOCKED"],
    "PR_GET_TIMERSLACK": ["NULL"],
    "PR_SET_TIMERSLACK": ["NULL"],
    "PR_TASK_PERF_EVENTS_DISABLE": ["NULL"],
    "PR_TASK_PERF_EVENTS_ENABLE": ["NULL"],
    "PR_CAPBSET_READ": ["0"],
    "PR_CAPBSET_DROP": ["0"],
    "PR_SET_CHILD_SUBREAPER": ["(int[]){1}"],
    "PR_GET_CHILD_SUBREAPER": ["NULL"],
    "PR_SET_NO_NEW_PRIVS": ["1"],
    "PR_GET_NO_NEW_PRIVS": ["NULL"],
    "PR_MCE_KILL": [("PR_MCE_KILL_CLEAR", "PR_MCE_KILL_LATE"), ("PR_MCE_KILL_SET", "PR_MCE_KILL_EARLY")],
    "PR_MCE_KILL_GET": [],
    "PR_SET_MM": [("PR_SET_MM_START_CODE", "0x400000"), ("PR_SET_MM_EXE_FILE", "0")],
    "PR_SET_PTRACER": ["0"],
    "PR_GET_TID_ADDRESS": ["NULL"],
    "PR_SET_THP_DISABLE": ["(int[]){1}"],
    "PR_GET_THP_DISABLE": ["NULL"],
    "PR_MPX_ENABLE_MANAGEMENT": [],
    "PR_MPX_DISABLE_MANAGEMENT": [],
    "PR_SET_FP_MODE": ["PR_FP_MODE_FR", "PR_FP_MODE_FRE"],
    "PR_GET_FP_MODE": [],
    "PR_CAP_AMBIENT": [("PR_CAP_AMBIENT_RAISE", "0")],
    "PR_SVE_SET_VL": ["0"],
    "PR_SVE_GET_VL": ["0"],
    "PR_GET_SPECULATION_CTRL": [("PR_SPEC_STORE_BYPASS", "PR_SPEC_ENABLE")],
    "PR_SET_SPECULATION_CTRL": ["PR_SPEC_STORE_BYPASS"],
    "PR_PAC_RESET_KEYS": ["PR_PAC_APIAKEY"],
    "PR_SET_TAGGED_ADDR_CTRL": ["PR_TAGGED_ADDR_ENABLE"],
    "PR_GET_TAGGED_ADDR_CTRL": [],
    "PR_SET_IO_FLUSHER": ["(int[]){1}"],
    "PR_GET_IO_FLUSHER": [],
    "PR_SET_SYSCALL_USER_DISPATCH_OFF": ["PR_SYS_DISPATCH_OFF"],
    "PR_SET_SYSCALL_USER_DISPATCH_ON": ["PR_SYS_DISPATCH_ON, 0, 4096, (char[]){1}"],
    "PR_SCHED_CORE": ["0, 0, PIDTYPE_PID, NULL"],
    "PR_SET_VMA": ["PR_SET_VMA_ANON_NAME, 0x1000, 4096, \"vma_name\""]
}

common_headers = """\
#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/prctl.h>
#include <signal.h>
"""

def write_c_file(name, code):
    with open(os.path.join(output_dir, f"{name}.c"), "w") as f:
        f.write(code)

def sanitize_filename(s):
    for c in '(){}[]"\\,':
        s = s.replace(c, '')
    return s.lower().replace(' ', '_')

def generate_prctl_tests():
    for option, args in prctl_options.items():
        if not args:
            file_name = f"prctl_{sanitize_filename(option)}"
            code = f"""{common_headers}
int main() {{
    syscall(SYS_prctl, {option});
    return 0;
}}
"""
            write_c_file(file_name, code)
        else:
            for arg in args:
                if isinstance(arg, tuple):
                    arg_str = ", ".join(arg)
                    file_name = f"prctl_{sanitize_filename(option)}_{sanitize_filename('_'.join(arg))}"
                else:
                    arg_str = arg
                    file_name = f"prctl_{sanitize_filename(option)}_{sanitize_filename(arg)}"

                code = f"""{common_headers}
int main() {{
    syscall(SYS_prctl, {option}, {arg_str});
    return 0;
}}
"""
                write_c_file(file_name, code)

generate_prctl_tests()
