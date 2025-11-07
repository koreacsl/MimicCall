
import os

def generate_setpriority_tests():
    output_dir = "./tool/cfiles/141_setpriority"
    os.makedirs(output_dir, exist_ok=True)

    priority_whos = {
        "PRIO_PROCESS": 0,
        "PRIO_PGRP": 1,
        "PRIO_USER": 2
    }

    for which_name, which_val in priority_whos.items():
        c_code = f"""#include <sys/resource.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_setpriority
#define SYS_setpriority 141
#endif
#ifndef SYS_getpriority
#define SYS_getpriority 140
#endif

#define {which_name} {which_val}

int main() {{
    int who = 0;

    int current_prio = syscall(SYS_getpriority, {which_name}, who);
    if (current_prio == -1) {{
        return 0;
    }}

    syscall(SYS_setpriority, {which_name}, who, 10);
    
    syscall(SYS_setpriority, {which_name}, who, current_prio);

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"setpriority_{which_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_setpriority_tests()
