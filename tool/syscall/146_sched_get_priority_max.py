
import os

def generate_sched_get_priority_max_tests():
    output_dir = "./tool/cfiles/146_sched_get_priority_max"
    os.makedirs(output_dir, exist_ok=True)

    sched_policies = [
        "SCHED_OTHER",
        "SCHED_FIFO",
        "SCHED_RR",
        "SCHED_BATCH",
        "SCHED_IDLE",
        "SCHED_DEADLINE"
    ]

    for policy in sched_policies:
        c_code = f"""#define _GNU_SOURCE
#include <sched.h>
#include <sys/syscall.h>

#ifndef SCHED_DEADLINE
#define SCHED_DEADLINE 6
#endif

int main() {{
    if (syscall(SYS_sched_get_priority_max, {policy}) == -1) {{
        return 1;
    }}
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"sched_get_priority_max_{policy.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_sched_get_priority_max_tests()
