import os

def generate_dup_test():
    output_dir = "./tool/cfiles/32_dup"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_dup
#define SYS_dup 32
#endif

int main() {
    int oldfd = open("/dev/null", O_RDONLY);
    if (oldfd == -1) {
        return 1;
    }

    int newfd = syscall(SYS_dup, oldfd);
    if (newfd == -1) {
        close(oldfd);
        return 1;
    }

    close(oldfd);
    close(newfd);

    return 0;
}
"""
    filename = f"{output_dir}/dup_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_dup_test()
