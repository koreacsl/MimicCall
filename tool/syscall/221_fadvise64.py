# -*- coding: utf-8 -*-
import os

def generate_fadvise64_tests():
    output_dir = "./tool/cfiles/221_fadvise64"
    os.makedirs(output_dir, exist_ok=True)

    fadvise_flags = [
        ("normal", "POSIX_FADV_NORMAL"),
        ("sequential", "POSIX_FADV_SEQUENTIAL"),
        ("random", "POSIX_FADV_RANDOM"),
        ("noreuse", "POSIX_FADV_NOREUSE"),
        ("willneed", "POSIX_FADV_WILLNEED"),
        ("dontneed", "POSIX_FADV_DONTNEED"),
    ]

    for name, flag in fadvise_flags:
        c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_fadvise64
#define SYS_fadvise64 221
#endif

#ifndef POSIX_FADV_NORMAL
#define POSIX_FADV_NORMAL 0
#endif
#ifndef POSIX_FADV_RANDOM
#define POSIX_FADV_RANDOM 1
#endif
#ifndef POSIX_FADV_SEQUENTIAL
#define POSIX_FADV_SEQUENTIAL 2
#endif
#ifndef POSIX_FADV_WILLNEED
#define POSIX_FADV_WILLNEED 3
#endif
#ifndef POSIX_FADV_DONTNEED
#define POSIX_FADV_DONTNEED 4
#endif
#ifndef POSIX_FADV_NOREUSE
#define POSIX_FADV_NOREUSE 5
#endif

int main() {{
    const char *path = "/tmp/test_fadvise_file";
    int fd = open(path, O_CREAT | O_RDWR, 0644);
    if (fd == -1) return 1;

    int result = syscall(SYS_fadvise64, fd, 0, 0, {flag});
    
    close(fd);
    unlink(path);
    return result == 0 ? 0 : 1;
}}
"""
        filename = os.path.join(output_dir, f"fadvise64_{name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_fadvise64_tests()
