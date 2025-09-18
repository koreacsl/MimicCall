import os

def generate_copy_file_range_tests():
    output_dir = "./tool/cfiles/326_copy_file_range"
    os.makedirs(output_dir, exist_ok=True)

    tests = [
        ("copy_file_range_null_offset", "NULL", "NULL"),
        ("copy_file_range_with_offset", "&in_offset", "&out_offset"),
        ("copy_file_range_partial", "NULL", "NULL", 512),
        ("copy_file_range_large", "NULL", "NULL", 4096),
    ]
    
    for syscall_name, off_in, off_out, *length in tests:
        len_bytes = length[0] if length else 1024
        c_code = f"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

#ifndef SYS_copy_file_range
#define SYS_copy_file_range 326
#endif

int main(void) {{
    int fd_in = open("testfile_in", O_CREAT | O_RDWR, 0644);
    int fd_out = open("testfile_out", O_CREAT | O_WRONLY | O_TRUNC, 0644);
    if (fd_in == -1 || fd_out == -1) {{
        perror("open");
        if (fd_in != -1) close(fd_in);
        if (fd_out != -1) close(fd_out);
        return 1;
    }}

    if (write(fd_in, "ABCD", 4) != 4) {{
        perror("write");
        close(fd_in); close(fd_out);
        return 1;
    }}
    if (lseek(fd_in, 0, SEEK_SET) == (off_t)-1) {{
        perror("lseek");
        close(fd_in); close(fd_out);
        return 1;
    }}

    off_t in_offset = 0, out_offset = 0;
    ssize_t n = syscall(SYS_copy_file_range, fd_in, {off_in}, fd_out, {off_out}, {len_bytes}, 0);
    if (n == -1) {{
        perror("copy_file_range");
        close(fd_in);
        close(fd_out);
        unlink("testfile_in");
        unlink("testfile_out");
        return 1;
    }}

    close(fd_in);
    close(fd_out);
    unlink("testfile_in");
    unlink("testfile_out");
    return 0;
}}
"""
        filename = f"{output_dir}/{syscall_name}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_copy_file_range_tests()
