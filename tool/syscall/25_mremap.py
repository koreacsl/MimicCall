import os

def generate_mremap_tests():
    output_dir = "./tool/cfiles/25_mremap"
    os.makedirs(output_dir, exist_ok=True)

    mremap_flags = {
        "MREMAP_MAYMOVE": "MREMAP_MAYMOVE",
        "MREMAP_FIXED": "MREMAP_FIXED",
        "MREMAP_DONTUNMAP": "MREMAP_DONTUNMAP"
    }

    for flag_name, flag_value in mremap_flags.items():
        c_code = f"""#define _GNU_SOURCE
#include <unistd.h>
#include <sys/mman.h>
#include <sys/syscall.h>

#ifndef SYS_mremap
#define SYS_mremap 25
#endif

#ifndef MREMAP_DONTUNMAP
#define MREMAP_DONTUNMAP 4
#endif

int main() {{
    void *addr = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) {{
        return 1;
    }}

    void *new_addr_hint = (strcmp("{flag_name}", "MREMAP_FIXED") == 0) ? (void*)((char*)addr + 4096) : NULL;

    void *new_addr = (void *)syscall(SYS_mremap, addr, 4096, 8192, {flag_value}, new_addr_hint);
    if (new_addr == MAP_FAILED) {{
        munmap(addr, 4096);
        return 1;
    }}

    if ("{flag_name}" == "MREMAP_DONTUNMAP"){{
        munmap(addr, 4096);
    }}
    
    munmap(new_addr, 8192);

    return 0;
}}
"""
        filename = f"{output_dir}/mremap_{flag_name.lower()}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_mremap_tests()
