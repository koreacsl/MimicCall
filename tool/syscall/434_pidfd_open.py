import os

def generate_pidfd_open_test():
    output_dir = "./tool/cfiles/434_pidfd_open"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/types.h>

#ifndef SYS_pidfd_open
#define SYS_pidfd_open 434
#endif

int main() {
    pid_t pid = getpid();

    int pidfd = syscall(SYS_pidfd_open, pid, 0);

    if (pidfd == -1) {
        return 1;
    }

    close(pidfd);

    return 0;
}
"""
    filename = f"{output_dir}/pidfd_open_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_pidfd_open_test()
