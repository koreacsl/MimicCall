import os

def generate_mlockall_tests():
    output_dir = "./tool/cfiles/151_mlockall"
    os.makedirs(output_dir, exist_ok=True)

    mlockall_flags = ["MCL_CURRENT", "MCL_FUTURE", "MCL_ONFAULT"]

    for flag in mlockall_flags:
        syscall_name = f"mlockall_{flag.lower()}"
        
        c_code = f"""#include <sys/mman.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_mlockall
#define SYS_mlockall 151
#endif

#ifndef MCL_ONFAULT
#define MCL_ONFAULT 4
#endif

int main() {{
    int result = syscall(SYS_mlockall, {flag});

    munlockall();

    if (result == -1) {{
        return 1;
    }}

    return 0;
}}
"""
        filename = f"{output_dir}/{syscall_name}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_mlockall_tests()
