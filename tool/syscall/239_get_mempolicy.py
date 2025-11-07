
import os

def generate_getmempolicy_tests():
    output_dir = "./tool/cfiles/239_get_mempolicy"
    os.makedirs(output_dir, exist_ok=True)

    mempolicy_flags = {
        "MPOL_F_NODE": (1 << 0),
        "MPOL_F_ADDR": (1 << 1),
        "MPOL_F_MEMS_ALLOWED": (1 << 2)
    }

    for flag_name, flag_value in mempolicy_flags.items():
        c_code = f"""#include <unistd.h>
#include <sys/syscall.h>
#include <linux/mempolicy.h>

#ifndef SYS_get_mempolicy
#define SYS_get_mempolicy 239
#endif

#ifndef {flag_name}
#define {flag_name} {flag_value}
#endif

int main() {{
    int mode;
    unsigned long nodemask;

    syscall(SYS_get_mempolicy, &mode, &nodemask, sizeof(nodemask) * 8, 0, {flag_name});

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"get_mempolicy_{flag_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_getmempolicy_tests()
