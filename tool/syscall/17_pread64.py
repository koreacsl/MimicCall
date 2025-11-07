import os
import sys

def generate_pread64_test():
    output_dir = "./tool/cfiles/17_pread64"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_pread64
#  define SYS_pread64 17
#endif

int main() {
    int fd = open("/dev/null", O_RDONLY);
    if (fd == -1) return 1;

    char buf[128];
    if (syscall(SYS_pread64, fd, buf, sizeof(buf), 0) == -1) {
        close(fd);
        return 1;
    }

    close(fd);
    return 0;
}
"""
    filename = f"{output_dir}/pread64_0.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_pread64_test()
