import os

def generate_select_test():
    output_dir = "./tool/cfiles/23_select"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
#include <unistd.h>
#include <sys/select.h>
#include <sys/time.h>
#include <sys/syscall.h>

#ifndef SYS_select
#define SYS_select 23
#endif

int main() {
    int pipefd[2];
    if (pipe(pipefd) == -1) {
        return 1;
    }

    fd_set readfds;
    FD_ZERO(&readfds);
    FD_SET(pipefd[0], &readfds);

    struct timeval timeout;
    timeout.tv_sec = 0;
    timeout.tv_usec = 1000;

    if (syscall(SYS_select, pipefd[0] + 1, &readfds, NULL, NULL, &timeout) == -1) {
        close(pipefd[0]);
        close(pipefd[1]);
        return 1;
    }

    close(pipefd[0]);
    close(pipefd[1]);
    return 0;
}
"""
    filename = f"{output_dir}/select_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_select_test()
