import os
import itertools

def generate_mbind_tests():
    output_dir = "./tool/cfiles/237_mbind"
    os.makedirs(output_dir, exist_ok=True)

    mbind_modes = [
        "MPOL_DEFAULT",
        "MPOL_BIND",
        "MPOL_INTERLEAVE",
        "MPOL_WEIGHTED_INTERLEAVE",
        "MPOL_PREFERRED",
        "MPOL_F_STATIC_NODES",
        "MPOL_F_RELATIVE_NODES",
        "MPOL_F_NUMA_BALANCING"
    ]

    mbind_flags = [
        "MPOL_MF_STRICT",
        "MPOL_MF_MOVE"
    ]

    common_header = r"""#define _GNU_SOURCE
#include <unistd.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <linux/mempolicy.h>
#include <errno.h>
#include <stdio.h>

#ifndef SYS_mbind
#define SYS_mbind 237
#endif

#ifndef MPOL_DEFAULT
#define MPOL_DEFAULT 0
#endif
#ifndef MPOL_PREFERRED
#define MPOL_PREFERRED 1
#endif
#ifndef MPOL_BIND
#define MPOL_BIND 2
#endif
#ifndef MPOL_INTERLEAVE
#define MPOL_INTERLEAVE 3
#endif

#ifndef MPOL_MF_STRICT
#define MPOL_MF_STRICT (1<<0)
#endif
#ifndef MPOL_MF_MOVE
#define MPOL_MF_MOVE   (1<<1)
#endif

static int do_mbind(void *addr, unsigned long len, int mode,
                    const unsigned long *mask, unsigned long maxnode_bits,
                    unsigned flags) {
    long ret = syscall(SYS_mbind, addr, len, mode, mask, maxnode_bits, flags);
    if (ret == -1) {
        perror("mbind");
        return -1;
    }
    return 0;
}
"""

    for mode in mbind_modes:
        syscall_name = f"mbind_{mode.lower()}"
        c_code = common_header + f"""
int main(void) {{
    void *addr = mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) {{
        perror("mmap");
        return 1;
    }}

    unsigned long nodemask[1] = {{ 1UL }};
    unsigned long maxnode_bits = sizeof(nodemask) * 8;

    int rc = do_mbind(addr, 4096, {mode}, nodemask, maxnode_bits, 0);
    munmap(addr, 4096);
    return rc == 0 ? 0 : 1;
}}
"""
        filename = f"{output_dir}/{syscall_name}.c"
        with open(filename, "w") as f:
            f.write(c_code)

    for r in range(1, len(mbind_flags) + 1):
        for flag_combination in itertools.combinations(mbind_flags, r):
            flags_str = " | ".join(flag_combination)
            flag_name = "_".join([flag.lower() for flag in flag_combination])
            syscall_name = f"mbind_flags_{flag_name}"

            c_code = common_header + f"""
int main(void) {{
    void *addr = mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) {{
        perror("mmap");
        return 1;
    }}

    unsigned long nodemask[1] = {{ 1UL }};
    unsigned long maxnode_bits = sizeof(nodemask) * 8;

    int rc = do_mbind(addr, 4096, MPOL_DEFAULT, nodemask, maxnode_bits, {flags_str});
    munmap(addr, 4096);
    return rc == 0 ? 0 : 1;
}}
"""
            filename = f"{output_dir}/{syscall_name}.c"
            with open(filename, "w") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_mbind_tests()
