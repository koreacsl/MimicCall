# -*- coding: utf-8 -*-
import os

def generate_fchdir_test():
    output_dir = "./tool/cfiles/81_fchdir"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_fchdir
#define SYS_fchdir 81
#endif

int main() {
    int fd = open("/tmp", O_RDONLY | O_DIRECTORY);
    if (fd == -1) {
        return 1;
    }

    int result = syscall(SYS_fchdir, fd);
    
    close(fd);

    return (result == -1) ? 1 : 0;
}
"""
    filename = os.path.join(output_dir, "fchdir_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_fchdir_test()
