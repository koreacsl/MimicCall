# -*- coding: utf-8 -*-
import os

def generate_mprotect_tests():
    output_dir = "./tool/cfiles/10_mprotect"
    os.makedirs(output_dir, exist_ok=True)

    mmap_prot_flags = [
        "PROT_NONE", "PROT_EXEC", "PROT_READ", "PROT_WRITE",
        "PROT_SEM", "PROT_GROWSDOWN", "PROT_GROWSUP"
    ]

    for prot_flag in mmap_prot_flags:
        flag_name = prot_flag.lower().replace("prot_", "")
        syscall_name = f"mprotect_{flag_name}"
        
        c_code = f"""#include <sys/mman.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_mprotect
#define SYS_mprotect 10
#endif

#ifndef PROT_SEM
#define PROT_SEM 0x8
#endif
#ifndef PROT_GROWSDOWN
#define PROT_GROWSDOWN 0x01000000
#endif
#ifndef PROT_GROWSUP
#define PROT_GROWSUP 0x02000000
#endif

int main() {{
    long page_size = sysconf(_SC_PAGESIZE);
    if (page_size == -1) {{
        return 1;
    }}

    void *addr = mmap(NULL, page_size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) {{
        return 1;
    }}

    int result = syscall(SYS_mprotect, addr, page_size, {prot_flag});

    munmap(addr, page_size);

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
    generate_mprotect_tests()
