# -*- coding: utf-8 -*-
import os

def generate_getpriority_tests():
    output_dir = "./tool/cfiles/140_getpriority"
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

#ifndef SYS_getpriority
#define SYS_getpriority 140
#endif

#define {which_name} {which_val}

int main() {{
    int who = 0;

    if (syscall(SYS_getpriority, {which_name}, who) == -1) {{
    }}

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"getpriority_{which_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_getpriority_tests()
