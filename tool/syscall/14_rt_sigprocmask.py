import os

def generate_rt_sigprocmask_tests():
    output_dir = "./tool/cfiles/14_rt_sigprocmask"
    os.makedirs(output_dir, exist_ok=True)

    how_flags = {
        "SIG_BLOCK": "block",
        "SIG_UNBLOCK": "unblock",
        "SIG_SETMASK": "setmask"
    }

    for flag, name in how_flags.items():
        c_code = f"""#define _GNU_SOURCE
#include <signal.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>

#ifndef KERNEL_SIGSET_BYTES
#define KERNEL_SIGSET_BYTES 8
#endif

int main(void) {{
    sigset_t set;
    sigemptyset(&set);
    sigaddset(&set, SIGUSR1);

    long ret = syscall(SYS_rt_sigprocmask, {flag}, &set, NULL, KERNEL_SIGSET_BYTES);
    if (ret == -1) {{
        perror("syscall(SYS_rt_sigprocmask)");
        return 1;
    }}
    return 0;
}}
"""
        filename = f"{output_dir}/rt_sigprocmask_{name}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_rt_sigprocmask_tests()