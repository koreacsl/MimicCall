import os

def generate_pselect6_test():
    output_dir = "./tool/cfiles/270_pselect6"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
#include <unistd.h>
#include <sys/select.h>
#include <time.h>
#include <signal.h>
#include <sys/syscall.h>

#ifndef SYS_pselect6
#define SYS_pselect6 270
#endif

int main() {
    int pipefd[2];
    if (pipe(pipefd) == -1) {
        return 1;
    }

    fd_set readfds;
    FD_ZERO(&readfds);
    FD_SET(pipefd[0], &readfds);

    struct timespec timeout;
    timeout.tv_sec = 0;
    timeout.tv_nsec = 1000000;

    sigset_t sigmask;
    sigemptyset(&sigmask);

    struct {
        const sigset_t *ss;
        size_t ss_len;
    } sig_data;
    
    sig_data.ss = &sigmask;
    sig_data.ss_len = sizeof(sigset_t);

    if (syscall(SYS_pselect6, pipefd[0] + 1, &readfds, NULL, NULL, &timeout, &sig_data) == -1) {
        close(pipefd[0]);
        close(pipefd[1]);
        return 1;
    }

    close(pipefd[0]);
    close(pipefd[1]);
    return 0;
}
"""
    filename = f"{output_dir}/pselect6_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_pselect6_test()
