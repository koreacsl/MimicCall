import os

def generate_clone_tests():
    output_dir = "./tool/cfiles/56_clone"
    os.makedirs(output_dir, exist_ok=True)

    clone_flags = [
        "CLONE_VM", "CLONE_FS", "CLONE_FILES", "CLONE_SIGHAND", "CLONE_PTRACE",
        "CLONE_VFORK", "CLONE_PARENT", "CLONE_THREAD", "CLONE_NEWNS", "CLONE_SYSVSEM",
        "CLONE_SETTLS", "CLONE_PARENT_SETTID", "CLONE_CHILD_CLEARTID", "CLONE_UNTRACED",
        "CLONE_CHILD_SETTID", "CLONE_NEWCGROUP", "CLONE_NEWUTS", "CLONE_NEWIPC",
        "CLONE_NEWUSER", "CLONE_NEWPID", "CLONE_NEWNET", "CLONE_IO", "CLONE_PIDFD"
    ]
    
    special_combos = {
        "CLONE_THREAD": ["CLONE_VM", "CLONE_SIGHAND", "CLONE_FILES", "CLONE_SYSVSEM", "CLONE_THREAD"],
        "CLONE_SIGHAND": ["CLONE_VM", "CLONE_SIGHAND"],
        "CLONE_VM": ["CLONE_VM"],
        "CLONE_PIDFD": ["CLONE_PIDFD"],
    }

    for flag in clone_flags:
        combo = special_combos.get(flag, [flag])
        flag_str = ' | '.join(combo)
        filename_suffix = flag.lower()
        
        c_code = f"""#define _GNU_SOURCE
#include <sched.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <sys/syscall.h>

#ifndef SYS_clone
#define SYS_clone 56
#endif

#define STACK_SIZE (1024 * 1024)

static int child_func(void *arg) {{
    return 0;
}}

int main() {{
    char *stack = malloc(STACK_SIZE);
    if (!stack) {{
        return 1;
    }}
    char *stack_top = stack + STACK_SIZE;
    
    pid_t child_pid = syscall(SYS_clone, {flag_str} | SIGCHLD, stack_top, NULL, NULL, NULL);

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
        filename = f"{output_dir}/clone_{filename_suffix}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_clone_tests()

