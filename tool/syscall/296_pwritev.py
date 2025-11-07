import os
import sys

def generate_pwritev_test():
    output_dir = "./tool/cfiles/296_pwritev"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <fcntl.h>
#include <unistd.h>
#include <sys/uio.h>
#include <sys/syscall.h>

#ifndef SYS_pwritev
#  define SYS_pwritev 296
#endif

int main() {
    int fd = open("/dev/null", O_WRONLY);
    if (fd == -1) return 1;

    char buf1[64] = "Hello, ";
    char buf2[64] = "World!";
    struct iovec iov[2] = {
        {buf1, sizeof(buf1)},
        {buf2, sizeof(buf2)}
    };

    if (syscall(SYS_pwritev, fd, iov, 2, 0) == -1) {
        close(fd);
        return 1;
    }

    close(fd);
    return 0;
}
"""
    filename = f"{output_dir}/pwritev_0.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_pwritev_test()
