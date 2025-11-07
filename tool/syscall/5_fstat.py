import os

def generate_fstat_test():
    output_dir = "./tool/cfiles/5_fstat"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <fcntl.h>
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <linux/stat.h>
#include <string.h>
#include <stdlib.h>
#include <sys/syscall.h>

#ifndef SYS_fstat
#define SYS_fstat 5
#endif

int main() {
    int fd = open("/dev/null", O_RDONLY);
    if (fd == -1) {
        return 1;
    }

    struct stat statbuf;
    if (syscall(SYS_fstat, fd, &statbuf) == -1) {
        close(fd);
        return 1;
    }

    close(fd);
    return 0;
}
"""
    filename = f"{output_dir}/fstat_0.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_fstat_test()
