import os

template = """#define _GNU_SOURCE
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/syscall.h>

void signal_handler(int sig) {
    printf("Received signal: %d\\n", sig);

    if (sig == SIGCHLD) {
        while (waitpid(-1, NULL, WNOHANG) > 0);
    }
}

int main() {
    struct sigaction act, oldact;
    memset(&act, 0, sizeof(act));

    act.sa_handler = signal_handler;
    act.sa_flags = {sigaction_flag};
    sigemptyset(&act.sa_mask);

    if (syscall(SYS_rt_sigaction, {signal_no}, &act, &oldact) == -1) {
        perror("rt_sigaction failed");
        return 1;
    }

    printf("Sending signal {signal_no}\\n");
    kill(getpid(), {signal_no});

    if (syscall(SYS_rt_sigaction, {signal_no}, &oldact, NULL) == -1) {
        perror("Failed to restore original signal handler");
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
        with open(filename, "w") as f:
            f.write(template.replace("{signal_no}", str(signal_no))
                            .replace("{sigaction_flag}", flag))
