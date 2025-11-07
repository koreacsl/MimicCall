
import os

def generate_move_pages_tests():
    output_dir = "./tool/cfiles/279_move_pages"
    os.makedirs(output_dir, exist_ok=True)

    move_pages_flags = {
        "MPOL_MF_MOVE": "(1 << 1)",
        "MPOL_MF_MOVE_ALL": "(1 << 2)",
    }

    for flag_name, flag_value in move_pages_flags.items():
        c_code = f"""#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <numaif.h>
#include <sys/mman.h>
#include <string.h>
#include <stdio.h>

#ifndef SYS_get_mempolicy
#define SYS_get_mempolicy 239
#endif
#ifndef SYS_move_pages
#define SYS_move_pages 279
#endif

#ifndef {flag_name}
#define {flag_name} {flag_value}
#endif

int main() {{
    long page_size = sysconf(_SC_PAGESIZE);
    if (page_size < 0) return 1;

    void *addr = mmap(NULL, page_size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) return 1;

    memset(addr, 0, page_size);

    int current_node = -1;
    if (syscall(SYS_get_mempolicy, &current_node, NULL, 0, addr, MPOL_F_NODE | MPOL_F_ADDR) == -1) {{
        munmap(addr, page_size);
        return 0;
    }}
    if (current_node < 0) {{
        munmap(addr, page_size);
        return 1;
    }}

    void *pages[1] = {{ addr }};
    int nodes[1] = {{ current_node }};
    int status[1] = {{ -1 }};

    if (syscall(SYS_move_pages, 0, 1, pages, nodes, status, {flag_name}) == -1) {{
        munmap(addr, page_size);
        return 1;
    }}

    munmap(addr, page_size);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"move_pages_{flag_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_move_pages_tests()
