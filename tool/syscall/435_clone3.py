# -*- coding: utf-8 -*-
import os

def generate_clone3_tests():
    output_dir = "./tool/cfiles/435_clone3"
    os.makedirs(output_dir, exist_ok=True)
    
    clone_flags = [
        "CLONE_VM", "CLONE_FS", "CLONE_FILES", "CLONE_SIGHAND", "CLONE_PTRACE",
        "CLONE_VFORK", "CLONE_PARENT", "CLONE_THREAD", "CLONE_NEWNS", "CLONE_SYSVSEM",
        "CLONE_SETTLS", "CLONE_PARENT_SETTID", "CLONE_CHILD_CLEARTID", "CLONE_UNTRACED",
        "CLONE_CHILD_SETTID", "CLONE_NEWCGROUP", "CLONE_NEWUTS", "CLONE_NEWIPC",
        "CLONE_NEWUSER", "CLONE_NEWPID", "CLONE_NEWNET", "CLONE_IO", "CLONE_PIDFD",
        "CLONE_CLEAR_SIGHAND", "CLONE_INTO_CGROUP"
    ]

    for flag in clone_flags:
        flags_to_set = {flag}
        if flag in ("CLONE_THREAD", "CLONE_SIGHAND", "CLONE_SETTLS", 
                    "CLONE_PARENT_SETTID", "CLONE_CHILD_CLEARTID", 
                    "CLONE_CHILD_SETTID"):
            flags_to_set.add("CLONE_VM")
        if flag == "CLONE_THREAD":
            flags_to_set.add("CLONE_SIGHAND")

        flag_str = " | ".join(flags_to_set)

        c_code = f"""#define _GNU_SOURCE
#include <sched.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/syscall.h>
#include <signal.h>

#ifndef SYS_clone3
#define SYS_clone3 435
#endif

#define STACK_SIZE (1024 * 1024)

struct clone_args {{
    __u64 flags;
    __u64 pidfd;
    __u64 child_tid;
    __u64 parent_tid;
    __u64 exit_signal;
    __u64 stack;
    __u64 stack_size;
    __u64 tls;
    __u64 set_tid;
    __u64 set_tid_size;
    __u64 cgroup;
}};

static int child_func(void *arg) {{
    return 0;
}}

int main() {{
    char *stack = malloc(STACK_SIZE);
    if (!stack) {{
        return 1;
    }}

    struct clone_args cl_args;
    memset(&cl_args, 0, sizeof(cl_args));
    cl_args.flags = {flag_str};
    cl_args.stack = (__u64)stack;
    cl_args.stack_size = STACK_SIZE;
    cl_args.exit_signal = SIGCHLD;

    pid_t child_pid = syscall(SYS_clone3, &cl_args, sizeof(cl_args));

    if (child_pid == -1) {{
        free(stack);
        return 1;
    }}

    if (child_pid > 0) {{
        waitpid(child_pid, NULL, 0);
    }}
    
    free(stack);
    return 0;
}}
"""
        filename = f"{output_dir}/clone3_{flag.lower()}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_clone3_tests()

