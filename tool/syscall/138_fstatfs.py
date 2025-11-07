import os
import sys

def generate_fstatfs_test():
    output_dir = "./tool/cfiles/138_fstatfs"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/vfs.h>
#include <sys/statfs.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_fstatfs
#  define SYS_fstatfs 138
#endif

int main() {
    struct statfs buf;
    int fd = open("/dev/null", O_RDONLY);
    if (fd == -1) return 1;

    if (syscall(SYS_fstatfs, fd, &buf) == -1) {
        close(fd);
        return 1;
    }

    close(fd);
    return 0;
}
"""
    filename = f"{output_dir}/fstatfs_0.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_fstatfs_test()
