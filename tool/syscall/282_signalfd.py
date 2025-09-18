
import os

def generate_signalfd_tests():
    output_dir = "./tool/cfiles/282_signalfd"
    os.makedirs(output_dir, exist_ok=True)

    c_code = r"""#include <signal.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/signalfd.h>
#include <errno.h>
#include <stdio.h>

#ifndef SYS_signalfd
#define SYS_signalfd 282
#endif
#ifndef SYS_rt_sigprocmask
#define SYS_rt_sigprocmask 14
#endif
#ifndef SYS_kill
#define SYS_kill 62
#endif

#define KERNEL_SIGSET_BYTES 8

int main(void) {
    sigset_t mask;
    int sfd;
    struct signalfd_siginfo fdsi;

    sigemptyset(&mask);
    sigaddset(&mask, SIGUSR1);

    if (syscall(SYS_rt_sigprocmask, SIG_BLOCK, &mask, NULL, KERNEL_SIGSET_BYTES) == -1) {
        perror("rt_sigprocmask");
        return 1;
    }

    sfd = (int)syscall(SYS_signalfd, -1, &mask, KERNEL_SIGSET_BYTES);
    if (sfd == -1) {
        perror("signalfd");
        return 1;
    }

    if (syscall(SYS_kill, getpid(), SIGUSR1) == -1) {
        perror("kill");
        close(sfd);
        return 1;
    }

    ssize_t n = read(sfd, &fdsi, sizeof(fdsi));
    if (n != (ssize_t)sizeof(fdsi)) {
        perror("read(signalfd)");
        close(sfd);
        return 1;
    }

    close(sfd);
    return 0;
}
"""
    filename = os.path.join(output_dir, "signalfd_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_signalfd_tests()
