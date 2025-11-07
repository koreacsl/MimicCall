
import os

def generate_unshare_tests():
    output_dir = "./tool/cfiles/272_unshare"
    os.makedirs(output_dir, exist_ok=True)

    unshare_flags = [
        "CLONE_FILES", "CLONE_FS", "CLONE_NEWCGROUP", "CLONE_NEWIPC", "CLONE_NEWNET",
        "CLONE_NEWNS", "CLONE_NEWPID", "CLONE_NEWUSER", "CLONE_NEWUTS", "CLONE_SYSVSEM",
        "CLONE_NEWTIME"
    ]

    for flag_str in unshare_flags:
        c_code = f"""#define _GNU_SOURCE
#include <sched.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_unshare
#define SYS_unshare 272
#endif

int main() {{
    syscall(SYS_unshare, {flag_str});

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"test_{flag_str.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_unshare_tests()
