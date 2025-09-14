# -*- coding: utf-8 -*-
import os

def generate_sched_setattr_tests():
    output_dir = "./tool/cfiles/314_sched_setattr"
    os.makedirs(output_dir, exist_ok=True)

    sched_policies = {
        "SCHED_NORMAL": 0,
        "SCHED_FIFO": 1,
        "SCHED_RR": 2,
        "SCHED_BATCH": 3,
        "SCHED_IDLE": 5,
        "SCHED_DEADLINE": 6,
    }
    sched_flags = {
        "none": "0",
        "reset_on_fork": "SCHED_FLAG_RESET_ON_FORK",
    }

    for policy_name, policy_value in sched_policies.items():
        for flag_name, flag_value in sched_flags.items():
            c_code = f"""#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/types.h>
#include <linux/sched.h>
#include <string.h>

#ifndef SYS_sched_getattr
#define SYS_sched_getattr 315
#endif
#ifndef SYS_sched_setattr
#define SYS_sched_setattr 314
#endif

#ifndef SCHED_FLAG_RESET_ON_FORK
#define SCHED_FLAG_RESET_ON_FORK 0x01
#endif

struct sched_attr {{
    __u32 size;
    __u32 sched_policy;
    __u64 sched_flags;
    __s32 sched_nice;
    __u32 sched_priority;
    __u64 sched_runtime;
    __u64 sched_deadline;
    __u64 sched_period;
}};

int main() {{
    struct sched_attr original_attr, new_attr;
    
    memset(&original_attr, 0, sizeof(original_attr));
    original_attr.size = sizeof(original_attr);
    if (syscall(SYS_sched_getattr, 0, &original_attr, sizeof(original_attr), 0) == -1) {{
        return 1;
    }}

    memset(&new_attr, 0, sizeof(new_attr));
    new_attr.size = sizeof(new_attr);
    new_attr.sched_policy = {policy_name};
    new_attr.sched_flags = {flag_value};
    
    // This may fail for non-root users, which is a safe and valid outcome.
    if (syscall(SYS_sched_setattr, 0, &new_attr, 0) == 0) {{
        // If setting succeeded, restore the original attributes to ensure no system impact.
        syscall(SYS_sched_setattr, 0, &original_attr, 0);
    }}

    return 0;
}}
"""
            filename = os.path.join(output_dir, f"sched_setattr_{policy_name.lower()}_{flag_name}.c")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_sched_setattr_tests()
