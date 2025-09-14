# -*- coding: utf-8 -*-
import os

def generate_lseek_tests():
    output_dir = "./tool/cfiles/lseek"
    os.makedirs(output_dir, exist_ok=True)

    seek_whence_flags = [
        ("lseek_set", "SEEK_SET"),
        ("lseek_cur", "SEEK_CUR"),
        ("lseek_end", "SEEK_END"),
        ("lseek_data", "SEEK_DATA"),
        ("lseek_hole", "SEEK_HOLE")
    ]

    for syscall_name, flag in seek_whence_flags:
        c_code = f"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>

int main() {{
    const char* testfile = "./testfile_lseek";
    int fd = open(testfile, O_RDWR | O_CREAT, 0644);
    if (fd == -1) return 1;

    if (lseek(fd, 10, {flag}) == -1) {{
        close(fd);
        unlink(testfile);
        return 1;
    }}

    close(fd);
    unlink(testfile);
    return 0;
}}
"""
        filename = f"{output_dir}/{syscall_name}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_lseek_tests()