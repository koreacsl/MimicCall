import os

template = """#define _GNU_SOURCE
#include <signal.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#define STACK_SIZE 4096

#ifndef SS_AUTODISARM
#define SS_AUTODISARM 2147483648
#endif

volatile sig_atomic_t received = 0;

void signal_handler(int sig) {
    printf("Child received signal: %d on alternate stack.\\n", sig);
    received = 1;
}

int main() {
    int pipefd[2];
    if (pipe(pipefd) == -1) {
        perror("pipe failed");
        return 1;
    }

    pid_t child_pid = fork();
    if (child_pid == -1) {
        perror("fork failed");
        return 1;
    }

    if (child_pid == 0) {
        close(pipefd[0]);

        stack_t ss, old_ss;
        memset(&ss, 0, sizeof(ss));

        ss.ss_sp = malloc(STACK_SIZE);
        if (!ss.ss_sp) {
            perror("malloc failed");
            return 1;
        }
        ss.ss_size = STACK_SIZE;
        ss.ss_flags = {sigaltstack_flag};

        printf("Child setting up sigaltstack with flag: {sigaltstack_flag}\\n");

        if (syscall(SYS_sigaltstack, &ss, &old_ss) == -1) {
            perror("sigaltstack failed");
            free(ss.ss_sp);
            return 1;
        }

        struct sigaction act;
        memset(&act, 0, sizeof(act));
        act.sa_handler = signal_handler;
        act.sa_flags = SA_ONSTACK;
        sigemptyset(&act.sa_mask);

        if (sigaction(SIGUSR1, &act, NULL) == -1) {
            perror("sigaction failed");
            free(ss.ss_sp);
            return 1;
        }

        write(pipefd[1], "R", 1);
        close(pipefd[1]);

        printf("Child waiting for SIGUSR1...\\n");

        while (!received) {
            pause();
        }

        free(ss.ss_sp);
        return 0;

    } else {
        close(pipefd[1]);

        char buf;
        read(pipefd[0], &buf, 1);
        close(pipefd[0]);

        sleep(0.5);

        printf("Parent sending SIGUSR1 to child (PID: %d)\\n", child_pid);
        if (kill(child_pid, SIGUSR1) == -1) {
            perror("kill failed");
            return 1;
        }

        printf("Parent waiting for child to complete...\\n");
        waitpid(child_pid, NULL, 0);
        printf("Child process terminated.\\n");
    }

    return 0;
}
"""

directory = "./tool/cfiles/131_sigaltstack"
os.makedirs(directory, exist_ok=True)

sigaltstack_flags = ["SS_ONSTACK", "SS_DISABLE", "SS_AUTODISARM"]

for flag in sigaltstack_flags:
    filename = os.path.join(directory, f"sigaltstack_{flag}.c")
    with open(filename, "w") as f:
        f.write(template.replace("{sigaltstack_flag}", flag))
