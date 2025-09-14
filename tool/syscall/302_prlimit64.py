# -*- coding: utf-8 -*-
import os

def generate_prlimit64_tests():
    output_dir = "./tool/cfiles/302_prlimit64"
    os.makedirs(output_dir, exist_ok=True)

    rlimit_types = [
        "RLIMIT_AS", "RLIMIT_CORE", "RLIMIT_CPU", "RLIMIT_DATA",
        "RLIMIT_FSIZE", "RLIMIT_LOCKS", "RLIMIT_MEMLOCK", "RLIMIT_MSGQUEUE",
        "RLIMIT_NICE", "RLIMIT_NOFILE", "RLIMIT_NPROC", "RLIMIT_RSS",
        "RLIMIT_RTPRIO", "RLIMIT_RTTIME", "RLIMIT_SIGPENDING", "RLIMIT_STACK"
    ]

    for rlimit_type in rlimit_types:
        c_code = f"""#define _GNU_SOURCE
#include <sys/resource.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef SYS_prlimit64
#define SYS_prlimit64 302
#endif

int main() {{
    struct rlimit old_limit, new_limit;
    pid_t pid = 0; 

    if (syscall(SYS_prlimit64, pid, {rlimit_type}, NULL, &old_limit) == -1) {{
        return 1;
    }}

    new_limit = old_limit;

    if (syscall(SYS_prlimit64, pid, {rlimit_type}, &new_limit, NULL) == -1) {{
    }}

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"prlimit64_{rlimit_type.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_prlimit64_tests()
