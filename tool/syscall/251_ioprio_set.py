# -*- coding: utf-8 -*-
import os

def generate_ioprio_set_tests():
    output_dir = "./tool/cfiles/251_ioprio_set"
    os.makedirs(output_dir, exist_ok=True)

    ioprio_which = {
        "process": ("IOPRIO_WHO_PROCESS", "getpid()"),
        "pgrp": ("IOPRIO_WHO_PGRP", "getpgrp()"),
        "user": ("IOPRIO_WHO_USER", "getuid()")
    }

    for name, (which_const, who_func) in ioprio_which.items():
        c_code = f"""#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_ioprio_get
#define SYS_ioprio_get 252
#endif
#ifndef SYS_ioprio_set
#define SYS_ioprio_set 251
#endif

#define IOPRIO_WHO_PROCESS 1
#define IOPRIO_WHO_PGRP    2
#define IOPRIO_WHO_USER    3

int main() {{
    int old_ioprio;

    old_ioprio = syscall(SYS_ioprio_get, {which_const}, {who_func});
    if (old_ioprio == -1) {{
        // If we can't get the priority, we can't safely test set.
        // This is a valid outcome for non-root users.
        return 0;
    }}

    // To test safely, we set the priority to its current value.
    // This is a no-op if run as root, and will fail safely with EPERM
    // for non-root users.
    syscall(SYS_ioprio_set, {which_const}, {who_func}, old_ioprio);

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"ioprio_set_{name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_ioprio_set_tests()
