import os
import sys

def generate_preadv_test():
    output_dir = "./tool/cfiles/295_preadv"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <fcntl.h>
#include <unistd.h>
#include <sys/uio.h>
#include <sys/syscall.h>

#ifndef SYS_preadv
#  define SYS_preadv 295
#endif

int main() {
    int fd = open("/dev/null", O_RDONLY);
    if (fd == -1) return 1;

    char buf1[64], buf2[64];
    struct iovec iov[2] = {
        {buf1, sizeof(buf1)},
        {buf2, sizeof(buf2)}
    };

    if (syscall(SYS_preadv, fd, iov, 2, 0) == -1) {
        close(fd);
        return 1;
    }

    close(fd);
    return 0;
}
"""
    filename = f"{output_dir}/preadv_0.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_preadv_test()
