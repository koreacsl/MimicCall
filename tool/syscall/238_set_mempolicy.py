# -*- coding: utf-8 -*-
import os

def generate_setmempolicy_tests():
    output_dir = "./tool/cfiles/238_set_mempolicy"
    os.makedirs(output_dir, exist_ok=True)

    mempolicy_modes = {
        "MPOL_DEFAULT": 0,
        "MPOL_BIND": 2,
        "MPOL_INTERLEAVE": 3,
        "MPOL_PREFERRED": 1,
    }

    for mode_name, mode_value in mempolicy_modes.items():
        c_code = f"""#include <unistd.h>
#include <sys/syscall.h>
#include <linux/mempolicy.h>

#ifndef SYS_set_mempolicy
#define SYS_set_mempolicy 238
#endif

#ifndef {mode_name}
#define {mode_name} {mode_value}
#endif

int main() {{
    unsigned long nodemask = 1;

    syscall(SYS_set_mempolicy, {mode_name}, &nodemask, sizeof(nodemask) * 8);

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"set_mempolicy_{mode_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_setmempolicy_tests()
