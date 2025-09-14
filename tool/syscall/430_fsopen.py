# -*- coding: utf-8 -*-
import os

def generate_fsopen_tests():
    output_dir = "./tool/cfiles/430_fsopen"
    os.makedirs(output_dir, exist_ok=True)

    filesystems = ["tmpfs", "sysfs"]
    fsopen_flags = {"none": "0", "cloexec": "FSOPEN_CLOEXEC"}

    for fs_name in filesystems:
        for flag_name, flag_value in fsopen_flags.items():
            c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/mount.h>

#ifndef SYS_fsopen
#define SYS_fsopen 430
#endif

int main() {{
    int fd = syscall(SYS_fsopen, "{fs_name}", {flag_value});
    if (fd >= 0) {{
        close(fd);
    }}
    return 0;
}}
"""
            filename = os.path.join(output_dir, f"fsopen_{fs_name}_{flag_name}.c")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_fsopen_tests()
