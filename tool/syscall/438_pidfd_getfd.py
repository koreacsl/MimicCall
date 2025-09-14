import os

def generate_pidfd_getfd_test():
    output_dir = "./tool/cfiles/438_pidfd_getfd"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <fcntl.h>

#ifndef SYS_pidfd_open
#define SYS_pidfd_open 434
#endif

#ifndef SYS_pidfd_getfd
#define SYS_pidfd_getfd 438
#endif

int main() {
    int target_fd = open("/dev/null", O_RDONLY);
    if (target_fd == -1) {
        return 1;
    }

    int pidfd = syscall(SYS_pidfd_open, getpid(), 0);
    if (pidfd == -1) {
        close(target_fd);
        return 1;
    }

    int new_fd = syscall(SYS_pidfd_getfd, pidfd, target_fd, 0);

    close(pidfd);
    close(target_fd);

    if (new_fd == -1) {
        return 1;
    }

    close(new_fd);

    return 0;
}
"""
    filename = f"{output_dir}/pidfd_getfd_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_pidfd_getfd_test()
