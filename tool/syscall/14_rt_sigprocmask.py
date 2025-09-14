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
        c_code = f"""#include <signal.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef SYS_rt_sigprocmask
#define SYS_rt_sigprocmask 14
#endif

int main() {{
    sigset_t set;
    
    sigemptyset(&set);
    sigaddset(&set, SIGUSR1);

    int result = syscall(SYS_rt_sigprocmask, {flag}, &set, NULL, sizeof(sigset_t));

    if (result == -1) {{
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
