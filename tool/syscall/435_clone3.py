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

        flag_str = " | ".join(sorted(flags_to_set))

        exit_sig = "0" if "CLONE_THREAD" in flags_to_set else "SIGCHLD"

        c_code = f"""#define _GNU_SOURCE
#include <sched.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/syscall.h>
#include <signal.h>
#include <stdint.h>

#ifndef SYS_clone3
#define SYS_clone3 435
#endif

#ifndef CLONE_CLEAR_SIGHAND
#define CLONE_CLEAR_SIGHAND  (1ULL << 32)
#endif
#ifndef CLONE_INTO_CGROUP
#define CLONE_INTO_CGROUP    (1ULL << 33)
#endif
#ifndef CLONE_PIDFD
#define CLONE_PIDFD          0x00001000
#endif

#define STACK_SIZE (1024 * 1024)

struct clone_args {{
    uint64_t flags;
    uint64_t pidfd;
    uint64_t child_tid;
    uint64_t parent_tid;
    uint64_t exit_signal;
    uint64_t stack;
    uint64_t stack_size;
    uint64_t tls;
    uint64_t set_tid;
    uint64_t set_tid_size;
    uint64_t cgroup;
}};

int main(void) {{
    void *stack = malloc(STACK_SIZE);
    if (!stack) {{
        return 1;
    }}

    struct clone_args cl_args;
    memset(&cl_args, 0, sizeof(cl_args));
    cl_args.flags = {flag_str};
    cl_args.stack = (uint64_t)stack;
    cl_args.stack_size = STACK_SIZE;
    cl_args.exit_signal = {exit_sig};

    pid_t child_pid = syscall(SYS_clone3, &cl_args, sizeof(cl_args));
    if (child_pid == -1) {{
        free(stack);
        return 1;
    }}

    if (child_pid > 0) {{
        (void)waitpid(child_pid, NULL, 0);
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
