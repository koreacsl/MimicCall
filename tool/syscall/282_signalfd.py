# -*- coding: utf-8 -*-
import os

def generate_signalfd_tests():
    output_dir = "./tool/cfiles/282_signalfd"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <signal.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/signalfd.h>

#ifndef SYS_signalfd
#define SYS_signalfd 282
#endif
#ifndef SYS_rt_sigprocmask
#define SYS_rt_sigprocmask 14
#endif
#ifndef SYS_kill
#define SYS_kill 62
#endif

int main() {
    sigset_t mask;
    int sfd;
    struct signalfd_siginfo fdsi;

    sigemptyset(&mask);
    sigaddset(&mask, SIGUSR1);

    if (syscall(SYS_rt_sigprocmask, SIG_BLOCK, &mask, NULL, sizeof(mask)) == -1) {
        return 1;
    }

    sfd = syscall(SYS_signalfd, -1, &mask, sizeof(mask));
    if (sfd == -1) {
        return 1;
    }

    syscall(SYS_kill, getpid(), SIGUSR1);

    if (read(sfd, &fdsi, sizeof(struct signalfd_siginfo)) != sizeof(struct signalfd_siginfo)) {
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
