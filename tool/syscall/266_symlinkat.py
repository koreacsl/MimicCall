# -*- coding: utf-8 -*-
import os

def generate_symlinkat_tests():
    output_dir = "./tool/cfiles/266_symlinkat"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_symlinkat
#define SYS_symlinkat 266
#endif

int main() {
    const char* target = "/tmp/symlinkat_test_target";
    const char* linkname = "symlinkat_test_link";
    const char* linkpath = "/tmp/symlinkat_test_link";

    unlink(target);
    unlink(linkpath);

    int fd = open(target, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        return 1;
    }
    close(fd);

    int dirfd = open("/tmp", O_RDONLY | O_DIRECTORY);
    if (dirfd == -1) {
        unlink(target);
        return 1;
    }

    if (syscall(SYS_symlinkat, target, dirfd, linkname) == -1) {
        close(dirfd);
        unlink(target);
        return 1;
    }

    close(dirfd);
    unlink(target);
    unlink(linkpath);

    return 0;
}
"""
    filename = os.path.join(output_dir, "symlinkat_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_symlinkat_tests()
