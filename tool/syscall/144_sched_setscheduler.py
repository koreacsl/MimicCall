# -*- coding: utf-8 -*-
import os

def generate_sched_setscheduler_tests():
    output_dir = "./tool/cfiles/144_sched_setscheduler"
    os.makedirs(output_dir, exist_ok=True)

    sched_policies = {
        "SCHED_OTHER": 0,
        "SCHED_FIFO": 1,
        "SCHED_RR": 2,
        "SCHED_BATCH": 3,
        "SCHED_IDLE": 5,
    }

    for policy_name, policy_val in sched_policies.items():
        c_code = f"""#include <sched.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_sched_setscheduler
#define SYS_sched_setscheduler 144
#endif
#ifndef SYS_sched_getscheduler
#define SYS_sched_getscheduler 145
#endif
#ifndef SYS_sched_getparam
#define SYS_sched_getparam 143
#endif

#define {policy_name} {policy_val}

int main() {{
    pid_t pid = getpid();
    struct sched_param orig_param;
    int orig_policy;

    orig_policy = syscall(SYS_sched_getscheduler, pid);
    if (orig_policy == -1) {{
        return 0;
    }}
    if (syscall(SYS_sched_getparam, pid, &orig_param) == -1) {{
        return 0;
    }}

    struct sched_param new_param = {{ .sched_priority = 0 }};
    if ({policy_name} != SCHED_OTHER) {{
        new_param.sched_priority = 1;
    }}

    syscall(SYS_sched_setscheduler, pid, {policy_name}, &new_param);
    
    syscall(SYS_sched_setscheduler, pid, orig_policy, &orig_param);

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"sched_setscheduler_{policy_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_sched_setscheduler_tests()
