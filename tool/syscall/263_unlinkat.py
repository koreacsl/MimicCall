# -*- coding: utf-8 -*-
import os

def generate_unlinkat_tests():
    output_dir = "./tool/cfiles/263_unlinkat"
    os.makedirs(output_dir, exist_ok=True)
    
    unlinkat_flags = {
        "none": ("0", False),
        "at_removedir": ("AT_REMOVEDIR", True)
    }

    for name, (flag, is_dir) in unlinkat_flags.items():
        if is_dir:
            setup_code = """
    const char* path = "/tmp/unlinkat_test_dir";
    rmdir(path); // Clean up previous
    if (mkdir(path, 0755) == -1) {
        return 1;
    }
"""
        else:
            setup_code = """
    const char* path = "/tmp/unlinkat_test_file";
    unlink(path); // Clean up previous
    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        return 1;
    }
    close(fd);
"""

        c_code = f"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/syscall.h>

#ifndef SYS_unlinkat
#define SYS_unlinkat 263
#endif

int main() {{
    {setup_code}

    if (syscall(SYS_unlinkat, AT_FDCWD, path, {flag}) == -1) {{
        return 1;
    }}

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"unlinkat_{name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_unlinkat_tests()
