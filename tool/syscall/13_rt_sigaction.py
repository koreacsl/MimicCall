import os

template = r"""#define _GNU_SOURCE
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <errno.h>
#include <sys/syscall.h>

#ifndef KERNEL_SIGSET_BYTES
#define KERNEL_SIGSET_BYTES 8
#endif

static void handler_basic(int sig) {
    if (sig == SIGCHLD) {
        while (waitpid(-1, NULL, WNOHANG) > 0) {}
    }
}

static void handler_info(int sig, siginfo_t *si, void *ucontext) {
    (void)ucontext;
    if (sig == SIGCHLD) {
        while (waitpid(-1, NULL, WNOHANG) > 0) {}
    }
}

int main(void) {
    struct sigaction act, oldact;
    memset(&act, 0, sizeof(act));
    sigemptyset(&act.sa_mask);

    act.sa_flags = {sigaction_flag};
{set_handler_line}

    long r1 = syscall(SYS_rt_sigaction, {signal_no}, &act, &oldact, KERNEL_SIGSET_BYTES);
    if (r1 == -1) {
        perror("syscall(SYS_rt_sigaction install)");
        return 1;
    }

    if (kill(getpid(), {signal_no}) == -1) {
        perror("kill failed");
        syscall(SYS_rt_sigaction, {signal_no}, &oldact, NULL, KERNEL_SIGSET_BYTES);
        return 1;
    }

    usleep(10000);

    long r2 = syscall(SYS_rt_sigaction, {signal_no}, &oldact, NULL, KERNEL_SIGSET_BYTES);
    if (r2 == -1) {
        perror("syscall(SYS_rt_sigaction restore)");
        return 1;
    }
    return 0;
}
"""

directory = "./tool/cfiles/13_rt_sigaction"
os.makedirs(directory, exist_ok=True)

signals = {
    "SIGINT": 2,
    "SIGTERM": 15,
    "SIGUSR1": 10,
    "SIGUSR2": 12,
    "SIGCHLD": 17
}

sigaction_flags = {
    "SA_NOCLDSTOP": ["SIGCHLD"],
    "SA_NOCLDWAIT": ["SIGCHLD"],
    "SA_NODEFER": ["SIGINT", "SIGTERM", "SIGUSR1", "SIGUSR2"],
    "SA_ONSTACK": ["SIGINT", "SIGTERM", "SIGUSR1", "SIGUSR2"],
    "SA_RESETHAND": ["SIGINT", "SIGTERM", "SIGUSR1", "SIGUSR2"],
    "SA_RESTART": ["SIGINT", "SIGTERM", "SIGUSR1", "SIGUSR2"],
    "SA_SIGINFO": ["SIGINT", "SIGTERM", "SIGUSR1", "SIGUSR2"]
}

for flag, applicable_signals in sigaction_flags.items():
    for signal_name in applicable_signals:
        signal_no = signals[signal_name]
        filename = os.path.join(directory, f"rt_sigaction_{signal_name}_{flag}.c")

        if flag == "SA_SIGINFO":
            set_handler_line = "    act.sa_sigaction = handler_info;"
        else:
            set_handler_line = "    act.sa_handler = handler_basic;"

        code = (template
                .replace("{signal_no}", str(signal_no))
                .replace("{sigaction_flag}", flag)
                .replace("{set_handler_line}", set_handler_line))

        with open(filename, "w") as f:
            f.write(code)