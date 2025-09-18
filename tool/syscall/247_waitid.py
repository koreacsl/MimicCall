import os

def parse_syscall_info(syscall_info):
    lines = syscall_info.strip().split("\n")
    syscall_defs = []
    options = {}

    for line in lines:
        if "(" in line:
            syscall_defs.append(line)
        elif "=" in line:
            key, values = line.split("= ")
            options[key.strip()] = values.split(", ")

    return syscall_defs, options

def generate_test_code(syscall_defs, options):
    test_cases = []

    for syscall_def in syscall_defs:
        if "P_PIDFD" in syscall_def:
            continue

        syscall_name, _ = syscall_def.split("(", 1)
        syscall_name = syscall_name.strip().split("$")[0]

        which_options = options.get("waitid_which", ["P_ALL"])
        valid_option_combos = ["WEXITED", "WEXITED | WNOHANG"]

        for which in which_options:
            for opt_str in valid_option_combos:
                test_code = f"""#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {{
    pid_t pid = fork();

    if (pid < 0) {{
        perror("fork failed");
        return 1;
    }}

    if (pid == 0) {{
        usleep(10000);
        exit(0);
    }} else {{
        siginfo_t info = {{0}};
        
        long target_pid = ({which} == P_PID) ? pid : 0;

        int ret = {syscall_name}({which}, target_pid, &info, {opt_str});

        if (ret == -1) {{
            perror("{syscall_name} failed");
        }} else {{
            if (info.si_pid == pid) {{
                printf("{syscall_name} succeeded for pid %d.\\n", info.si_pid);
            }} else {{
                 printf("{syscall_name} succeeded, but for unexpected pid %d.\\n", info.si_pid);
            }}
        }}
    }}

    return 0;
}}"""
                test_cases.append(test_code)

    return test_cases

syscall_info = """
waitid(which flags[waitid_which], pid pid, infop ptr[out, siginfo, opt], options flags[wait_options], ru ptr[out, rusage, opt])
waitid$P_PIDFD(which const[P_PIDFD], pidfd fd_pidfd, infop ptr[out, siginfo, opt], options flags[wait_options], ru ptr[out, rusage, opt])

waitid_which = P_PID, P_PGID, P_ALL
wait_options = WNOHANG, WUNTRACED, WCONTINUED, WEXITED, WSTOPPED, WCONTINUED, WNOHANG, WNOWAIT, __WCLONE, __WALL, __WNOTHREAD
"""

syscall_defs, options = parse_syscall_info(syscall_info)

test_codes = generate_test_code(syscall_defs, options)

target_dir = "./tool/cfiles/247_waitid"
os.makedirs(target_dir, exist_ok=True)


for i, code in enumerate(test_codes):
    filename = os.path.join(target_dir, f"waitid_{i}.c")
    with open(filename, "w") as f:
        f.write(code)
