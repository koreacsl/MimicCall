# -*- coding: utf-8 -*-
import os

def generate_fsync_tests():
    output_dir = "./tool/cfiles/74_fsync"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_fsync
#define SYS_fsync 74
#endif

int main() {
    int fd = open("/dev/null", O_WRONLY);
    if (fd == -1) {
        return 1;
    }

    int result = syscall(SYS_fsync, fd);

    close(fd);
    
    return (result == -1) ? 1 : 0;
}
"""
    filename = os.path.join(output_dir, "fsync_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_fsync_tests()
