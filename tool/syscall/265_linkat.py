# -*- coding: utf-8 -*-
import os

def generate_linkat_tests():
    output_dir = "./tool/cfiles/265_linkat"
    os.makedirs(output_dir, exist_ok=True)
    
    linkat_flags = {
        "none": "0",
        "at_empty_path": "AT_EMPTY_PATH",
        "at_symlink_follow": "AT_SYMLINK_FOLLOW"
    }

    for name, flag in linkat_flags.items():
        c_code = f"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_linkat
#define SYS_linkat 265
#endif

int main() {{
    const char* oldname = "linkat_test_old";
    const char* newname = "linkat_test_new";
    const char* oldpath = "/tmp/linkat_test_old";
    const char* newpath = "/tmp/linkat_test_new";

    unlink(oldpath);
    unlink(newpath);

    int fd = open(oldpath, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {{
        return 1;
    }}
    close(fd);
    
    int dirfd = open("/tmp", O_RDONLY | O_DIRECTORY);
    if (dirfd == -1) {{
        unlink(oldpath);
        return 1;
    }}

    if (syscall(SYS_linkat, dirfd, oldname, dirfd, newname, {flag}) == -1) {{
        close(dirfd);
        unlink(oldpath);
        return 1;
    }}

    close(dirfd);
    unlink(oldpath);
    unlink(newpath);

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"linkat_{name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_linkat_tests()
