
import os

def generate_pkey_alloc_tests():
    output_dir = "./tool/cfiles/330_pkey_alloc"
    os.makedirs(output_dir, exist_ok=True)

    pkey_flags = {
        "none": "0",
        "disable_access": "PKEY_DISABLE_ACCESS",
        "disable_write": "PKEY_DISABLE_WRITE"
    }

    for flag_name, flag_value in pkey_flags.items():
        c_code = f"""#include <unistd.h>
#include <sys/syscall.h>
#include <sys/mman.h>

#ifndef SYS_pkey_alloc
#define SYS_pkey_alloc 330
#endif
#ifndef SYS_pkey_free
#define SYS_pkey_free 331
#endif

#ifndef PKEY_DISABLE_ACCESS
#define PKEY_DISABLE_ACCESS 0x1
#endif
#ifndef PKEY_DISABLE_WRITE
#define PKEY_DISABLE_WRITE 0x2
#endif

int main() {{
    int pkey = syscall(SYS_pkey_alloc, 0, {flag_value});
    if (pkey == -1) {{
        return 0;
    }}

    syscall(SYS_pkey_free, pkey);

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"pkey_alloc_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_pkey_alloc_tests()
