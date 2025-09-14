# -*- coding: utf-8 -*-
import os

def generate_mmap_tests():
    output_dir = "./tool/cfiles/9_mmap"
    os.makedirs(output_dir, exist_ok=True)

    mmap_prot = [
        "PROT_EXEC", "PROT_READ", "PROT_WRITE", "PROT_SEM",
        "PROT_GROWSDOWN", "PROT_GROWSUP"
    ]

    mmap_flags = [
        "MAP_SHARED", "MAP_PRIVATE", "MAP_32BIT", "MAP_ANONYMOUS",
        "MAP_DENYWRITE", "MAP_EXECUTABLE", "MAP_FILE", "MAP_FIXED",
        "MAP_GROWSDOWN", "MAP_HUGETLB", "MAP_LOCKED", "MAP_NONBLOCK",
        "MAP_NORESERVE", "MAP_POPULATE", "MAP_STACK", "MAP_UNINITIALIZED",
        "MAP_SHARED_VALIDATE", "MAP_SYNC", "MAP_FIXED_NOREPLACE"
    ]

    for prot in mmap_prot:
        for flag in mmap_flags:
            base_map_flag = "MAP_PRIVATE"
            if flag in ["MAP_SHARED", "MAP_SHARED_VALIDATE"]:
                base_map_flag = "0"
            elif flag == "MAP_PRIVATE":
                base_map_flag = "0"

            c_code = f"""#include <sys/mman.h>
#include <unistd.h>
#include <stddef.h>
#include <sys/syscall.h>

#ifndef {prot}
#define {prot} 0
#endif

#ifndef {flag}
#define {flag} 0
#endif

#ifndef MAP_SHARED_VALIDATE
#define MAP_SHARED_VALIDATE 0x03
#endif
#ifndef MAP_SYNC
#define MAP_SYNC 0x080000
#endif
#ifndef MAP_FIXED_NOREPLACE
#define MAP_FIXED_NOREPLACE 0x100000
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

    int protection = {prot};
    int flags = {flag} | MAP_ANONYMOUS | {base_map_flag};

    void *addr = syscall(SYS_mmap, NULL, page_size, protection, flags, -1, 0);

    if (addr == MAP_FAILED) {{
        return 0;
    }}

    if (munmap(addr, page_size) == -1) {{
        return 1;
    }}

    return 0;
}}
"""
            filename = f"{output_dir}/mmap_{prot.lower()}_{flag.lower()}.c"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_mmap_tests()
