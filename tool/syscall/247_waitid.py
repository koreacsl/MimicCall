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
        syscall_name, args = syscall_def.split("(", 1)
        syscall_name = syscall_name.strip().split("$")[0]
        args = args.rstrip(")").split(", ")

        which_options = options.get("waitid_which", ["P_ALL"])
        wait_options = options.get("wait_options", ["0"])
        pid_values = ["0", "-1"]

        for which in which_options:
            for pid in pid_values:
                for opt in wait_options:
                    test_code = f"""#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>

int main() {{
    siginfo_t info;
    int ret = {syscall_name}({which}, {pid}, &info, {opt});

    if (ret == -1) {{
        perror("{syscall_name} failed");
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
