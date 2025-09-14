# -*- coding: utf-8 -*-
import os

def generate_fsconfig_tests():
    output_dir = "./tool/cfiles/431_fsconfig"
    os.makedirs(output_dir, exist_ok=True)

    test_cases = {
        "set_flag_sync": 'syscall(SYS_fsconfig, fd, FSCONFIG_SET_FLAG, "sync", NULL, 0);',
        "set_string_size": 'syscall(SYS_fsconfig, fd, FSCONFIG_SET_STRING, "size", "128k", 0);',
        "cmd_create": 'syscall(SYS_fsconfig, fd, FSCONFIG_CMD_CREATE, NULL, NULL, 0);'
    }

    for test_name, syscall_line in test_cases.items():
        c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/mount.h>

#ifndef SYS_fsopen
#define SYS_fsopen 430
#endif
#ifndef SYS_fsconfig
#define SYS_fsconfig 431
#endif

int main() {{
    int fd = syscall(SYS_fsopen, "tmpfs", 0);
    if (fd < 0) return 1;

    // This may require root privileges. Failure is an acceptable outcome.
    {syscall_line}

    close(fd);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"fsconfig_{test_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_fsconfig_tests()
