
import os

def generate_ioprio_get_tests():
    output_dir = "./tool/cfiles/252_ioprio_get"
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

#define IOPRIO_WHO_PROCESS 1
#define IOPRIO_WHO_PGRP    2
#define IOPRIO_WHO_USER    3

int main() {{
    syscall(SYS_ioprio_get, {which_const}, {who_func});

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"ioprio_get_{name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_ioprio_get_tests()
