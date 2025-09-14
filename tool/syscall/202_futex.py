import os

output_dir = "./tool/cfiles/202_futex"
os.makedirs(output_dir, exist_ok=True)

futex_ops = [
    "FUTEX_WAIT", "FUTEX_WAKE", "FUTEX_FD", "FUTEX_REQUEUE",
    "FUTEX_CMP_REQUEUE", "FUTEX_WAKE_OP", "FUTEX_LOCK_PI", "FUTEX_UNLOCK_PI",
    "FUTEX_TRYLOCK_PI", "FUTEX_WAIT_BITSET", "FUTEX_WAKE_BITSET",
    "FUTEX_WAIT_REQUEUE_PI", "FUTEX_CMP_REQUEUE_PI", "FUTEX_LOCK_PI2",
    "FUTEX_PRIVATE_FLAG", "FUTEX_CLOCK_REALTIME"
]

common_headers = """\
#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/futex.h>
#include <stdint.h>
#include <time.h>

#ifndef SYS_futex
#define SYS_futex 202
#endif
"""

def write_c_file(name, content):
    with open(os.path.join(output_dir, f"{name}.c"), "w") as f:
        f.write(content)

def generate_futex_tests():
    for op in futex_ops:
        name = f"futex_op_{op.lower()}"
        content = f"""{common_headers}
int main() {{
    int addr = 0;
    int addr2 = 0;
    struct timespec ts = {{ .tv_sec = 0, .tv_nsec = 1000000 }};
    syscall(SYS_futex, &addr, {op}, 1, &ts, &addr2, 1);
    return 0;
}}
"""
        write_c_file(name, content)

generate_futex_tests()
