import os

def generate_pidfd_send_signal_test():
    output_dir = "./tool/cfiles/424_pidfd_send_signal"
    os.makedirs(output_dir, exist_ok=True)

    c_code = r"""#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <signal.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>

#ifndef SYS_pidfd_open
#define SYS_pidfd_open 434
#endif

#ifndef SYS_pidfd_send_signal
#define SYS_pidfd_send_signal 424
#endif

static volatile sig_atomic_t got_usr1 = 0;

static void on_sigusr1(int signo) {
    (void)signo;
    got_usr1 = 1;
}

int main(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = on_sigusr1;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    if (sigaction(SIGUSR1, &sa, NULL) == -1) {
        perror("sigaction");
        return 1;
    }

    int pidfd = (int)syscall(SYS_pidfd_open, getpid(), 0);
    if (pidfd == -1) {
        perror("pidfd_open");
        return 1;
    }

    int result = (int)syscall(SYS_pidfd_send_signal, pidfd, SIGUSR1, NULL, 0);
    if (result == -1) {
        perror("pidfd_send_signal");
        close(pidfd);
        return 1;
    }

    for (int i = 0; i < 1000 && !got_usr1; ++i) {
        usleep(1000);
    }

    close(pidfd);

    if (!got_usr1) {
        fprintf(stderr, "SIGUSR1 not observed\n");
        return 1;
    }

    return 0;
}
"""
    filename = f"{output_dir}/pidfd_send_signal_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_pidfd_send_signal_test()
