import os

def generate_madvise_tests():
    output_dir = "./tool/cfiles/madvise"
    os.makedirs(output_dir, exist_ok=True)

    madvise_flags = {
        "MADV_NORMAL": 0, "MADV_RANDOM": 1, "MADV_SEQUENTIAL": 2, "MADV_WILLNEED": 3, "MADV_DONTNEED": 4,
        "MADV_REMOVE": 9, "MADV_DONTFORK": 10, "MADV_DOFORK": 11, "MADV_MERGEABLE": 12, "MADV_UNMERGEABLE": 13,
        "MADV_HUGEPAGE": 14, "MADV_NOHUGEPAGE": 15, "MADV_DONTDUMP": 16, "MADV_DODUMP": 17, "MADV_WIPEONFORK": 18,
        "MADV_KEEPONFORK": 19, "MADV_COLD": 20, "MADV_PAGEOUT": 21, "MADV_POPULATE_READ": 22, "MADV_POPULATE_WRITE": 23,
        "MADV_HWPOISON": 100, "MADV_SOFT_OFFLINE": 101
    }

    for flag_name, flag_value in madvise_flags.items():
        c_code = f"""#include <sys/mman.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_madvise
#define SYS_madvise 28
#endif

#ifndef {flag_name}
#define {flag_name} {flag_value}
#endif

int main() {{
    void *addr = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) {{
        return 1;
    }}

    if (syscall(SYS_madvise, addr, 4096, {flag_name}) == -1) {{
        munmap(addr, 4096);
        return 1;
    }}

    munmap(addr, 4096);
    return 0;
}}
"""
        filename = f"{output_dir}/madvise_{flag_name.lower()}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_madvise_tests()
