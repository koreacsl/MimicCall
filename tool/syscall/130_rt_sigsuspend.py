import os

template = template = """#define _GNU_SOURCE
#include <signal.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

void signal_handler(int sig) {
    printf("Child received signal: %d. Exiting sigsuspend.\\n", sig);
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

        struct sigaction act;
        memset(&act, 0, sizeof(act));
        act.sa_handler = signal_handler;
        sigemptyset(&act.sa_mask);
        act.sa_flags = 0;

        if (sigaction(SIGINT, &act, NULL) == -1) {
            perror("sigaction failed");
            return 1;
        }

        write(pipefd[1], "R", 1);
        close(pipefd[1]);

        sigset_t mask;
        sigemptyset(&mask);
        sigaddset(&mask, SIGINT);

        syscall(SYS_rt_sigsuspend, &mask, sizeof(sigset_t));

        return 0;
    } else {
        close(pipefd[1]);

        char buf;
        read(pipefd[0], &buf, 1);
        close(pipefd[0]);

        if (kill(child_pid, SIGINT) == -1) {
            perror("kill failed");
            return 1;
        }

        waitpid(child_pid, NULL, 0);
        printf("Child process terminated.\\n");
    }

    return 0;
}
"""

directory = "./tool/cfiles/130_rt_sigsuspend"
os.makedirs(directory, exist_ok=True)

filename = os.path.join(directory, "rt_sigsuspend_0.c")

with open(filename, "w") as f:
    f.write(template)
