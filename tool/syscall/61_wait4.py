import os

def parse_syscall_info(syscall_info):
    lines = syscall_info.strip().split("\n")
    syscall_def = lines[0]
    options_line = next((line for line in lines if "=" in line), "")

    syscall_name, args = syscall_def.split("(", 1)
    args = args.rstrip(")").split(", ")

    options = options_line.split("= ")[1].split(", ") if options_line else []
    if not options:
        options = ["0"]

    return syscall_name.strip(), options

def generate_test_code(syscall_name, options):
    test_cases = []
    pid_values = ["0", "-1"]

    for pid in pid_values:
        for option in options:
            test_code = f"""#include <sys/types.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <stdio.h>
#include <stdlib.h>

int main() {{
    int status = 0;
    struct rusage ru;
    int ret = {syscall_name}({pid}, &status, {option}, &ru);

    if (ret == -1) {{
        perror("{syscall_name} failed");
    }}

    return 0;
}}"""
            test_cases.append(test_code)

    return test_cases

syscall_info = """
wait4(pid pid, status ptr[out, int32, opt], options flags[wait_options], ru ptr[out, rusage, opt])

wait_options = WNOHANG, WUNTRACED, WCONTINUED, WEXITED, WSTOPPED, WNOWAIT, __WCLONE, __WALL, __WNOTHREAD
"""

syscall_name, options = parse_syscall_info(syscall_info)

test_codes = generate_test_code(syscall_name, options)

target_dir = "./tool/cfiles/61_wait4"
os.makedirs(target_dir, exist_ok=True)


for i, code in enumerate(test_codes):
    filename = os.path.join(target_dir, f"wait4_{i}.c")
    with open(filename, "w") as f:
        f.write(code)
