# -*- coding: utf-8 -*-
import os

def generate_sched_setaffinity_tests():
    output_dir = "./tool/cfiles/203_sched_setaffinity"
    os.makedirs(output_dir, exist_ok=True)

    # Test setting affinity for a couple of CPU cores
    cpu_cores = [0, 1] 

    for core in cpu_cores:
        c_code = f"""#define _GNU_SOURCE
#include <sched.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_sched_getaffinity
#define SYS_sched_getaffinity 204
#endif
#ifndef SYS_sched_setaffinity
#define SYS_sched_setaffinity 203
#endif

int main() {{
    pid_t pid = getpid();
    cpu_set_t original_mask, new_mask;

    // First, get the original affinity mask to restore it later.
    if (syscall(SYS_sched_getaffinity, pid, sizeof(original_mask), &original_mask) == -1) {{
        return 1;
    }}

    // Set the new affinity to a specific core.
    CPU_ZERO(&new_mask);
    CPU_SET({core}, &new_mask);
    if (syscall(SYS_sched_setaffinity, pid, sizeof(new_mask), &new_mask) == -1) {{
        // If setting fails (e.g., due to permissions), that's still a valid test outcome.
        // We don't need to restore in this case.
        return 0;
    }}

    // IMPORTANT: Restore the original affinity to leave the system unchanged.
    syscall(SYS_sched_setaffinity, pid, sizeof(original_mask), &original_mask);

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"sched_setaffinity_core_{core}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_sched_setaffinity_tests()
