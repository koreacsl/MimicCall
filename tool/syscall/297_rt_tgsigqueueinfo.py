# -*- coding: utf-8 -*-
import os

def generate_rt_tgsigqueueinfo_test():
    output_dir = "./tool/cfiles/297_rt_tgsigqueueinfo"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
#include <signal.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <string.h>
#include <sys/types.h>

#ifndef SYS_rt_tgsigqueueinfo
#define SYS_rt_tgsigqueueinfo 297
#endif
#ifndef SYS_gettid
#define SYS_gettid 186
#endif

volatile sig_atomic_t signal_received = 0;

void signal_handler(int sig, siginfo_t *info, void *context) {
    if (info->si_code == SI_QUEUE) {
        signal_received = 1;
    }
}

int main() {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_sigaction = signal_handler;
    sa.sa_flags = SA_SIGINFO;
    sigemptyset(&sa.sa_mask);

    if (sigaction(SIGUSR1, &sa, NULL) == -1) {
        return 1;
    }

    siginfo_t info;
    memset(&info, 0, sizeof(info));
    info.si_signo = SIGUSR1;
    info.si_code = SI_QUEUE;
    info.si_int = 1234;

    pid_t current_pid = getpid();
    pid_t current_tid = syscall(SYS_gettid);

    if (syscall(SYS_rt_tgsigqueueinfo, current_pid, current_tid, SIGUSR1, &info) == -1) {
        return 1;
    }

    sleep(1);

    if (signal_received == 1) {
        return 0;
    }

    return 1;
}
"""
    filename = os.path.join(output_dir, "rt_tgsigqueueinfo_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_rt_tgsigqueueinfo_test()
