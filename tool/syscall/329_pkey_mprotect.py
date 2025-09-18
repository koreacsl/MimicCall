
import os

def generate_pkey_mprotect_tests():
    output_dir = "./tool/cfiles/329_pkey_mprotect"
    os.makedirs(output_dir, exist_ok=True)
    
    mmap_prot_flags = {
        "read": "PROT_READ",
        "write": "PROT_WRITE",
        "exec": "PROT_EXEC"
    }

    for prot_name, prot_value in mmap_prot_flags.items():
        c_code = f"""#include <sys/mman.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_pkey_alloc
#define SYS_pkey_alloc 330
#endif
#ifndef SYS_pkey_free
#define SYS_pkey_free 331
#endif
#ifndef SYS_pkey_mprotect
#define SYS_pkey_mprotect 329
#endif

int main() {{
    int pkey = syscall(SYS_pkey_alloc, 0, 0);
    if (pkey == -1) {{
        return 0;
    }}

    void *addr = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) {{
        syscall(SYS_pkey_free, pkey);
        return 1;
    }}

    syscall(SYS_pkey_mprotect, addr, 4096, {prot_value}, pkey);
    
    munmap(addr, 4096);
    syscall(SYS_pkey_free, pkey);
    
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"pkey_mprotect_{prot_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_pkey_mprotect_tests()
