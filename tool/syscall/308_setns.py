# -*- coding: utf-8 -*-
import os

def generate_setns_tests():
    output_dir = "./tool/cfiles/308_setns"
    os.makedirs(output_dir, exist_ok=True)

    # Flags for the 'nstype' argument of setns
    ns_type_flags = {
        "none": "0",
        "ipc": "CLONE_NEWIPC",
        "net": "CLONE_NEWNET",
        "uts": "CLONE_NEWUTS",
        "cgroup": "CLONE_NEWCGROUP",
        "ns": "CLONE_NEWNS",
        "pid": "CLONE_NEWPID",
        "user": "CLONE_NEWUSER",
        "time": "CLONE_NEWTIME"
    }

    for flag_name, flag_value in ns_type_flags.items():
        c_code = f"""#define _GNU_SOURCE
#include <sched.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_setns
#define SYS_setns 308
#endif

int main() {{
    int fd = open("/proc/self/ns/mnt", O_RDONLY);
    if (fd == -1) {{
        return 1;
    }}

    syscall(SYS_setns, fd, {flag_value});
    
    close(fd);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"setns_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_setns_tests()
