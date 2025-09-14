import os
import itertools

def generate_mbind_tests():
    output_dir = "./tool/cfiles/237_mbind"

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

    for mode in mbind_modes:
        syscall_name = f"mbind_{mode.lower()}"
        c_code = f"""#define _GNU_SOURCE
#include <numaif.h>
#include <sys/mman.h>
#include <unistd.h>

#ifndef MPOL_F_RELATIVE_NODES
#define MPOL_F_RELATIVE_NODES 16384
#endif

#ifndef MPOL_F_STATIC_NODES
#define MPOL_F_STATIC_NODES 32768
#endif

int main() {{
    void *addr = mmap(0, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) return 1;

    unsigned long nodemask = 1;
    int result = mbind(addr, 4096, {mode}, &nodemask, 1, 0);

    return result == -1 ? 1 : 0;
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
            
            c_code = f"""#define _GNU_SOURCE
#include <numaif.h>
#include <sys/mman.h>
#include <unistd.h>

#ifndef MPOL_F_RELATIVE_NODES
#define MPOL_F_RELATIVE_NODES 16384
#endif

#ifndef MPOL_F_STATIC_NODES
#define MPOL_F_STATIC_NODES 32768
#endif

int main() {{
    void *addr = mmap(0, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) return 1;

    unsigned long nodemask = 1;
    int result = mbind(addr, 4096, MPOL_DEFAULT, &nodemask, 1, {flags_str});

    return result == -1 ? 1 : 0;
}}
"""
            filename = f"{output_dir}/{syscall_name}.c"
            with open(filename, "w") as f:
                f.write(c_code)

if __name__ == "__main__":
    output_dir = "./tool/cfiles/237_mbind"
    os.makedirs(output_dir, exist_ok=True)
    generate_mbind_tests()