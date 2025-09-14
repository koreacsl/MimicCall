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

        sigset_t set;
        sigemptyset(&set);
        sigaddset(&set, SIGINT);

        if (syscall(SYS_rt_sigprocmask, SIG_BLOCK, &set, NULL, 8) == -1) {
            perror("rt_sigprocmask failed");
            return 1;
        }

        write(pipefd[1], "R", 1);
        close(pipefd[1]);

        printf("Child process (PID: %d) waiting for SIGINT (it will be pending)...\\n", getpid());

        sleep(1);

        sigset_t pending_set;
        if (syscall(SYS_rt_sigpending, &pending_set, 8) == -1) {
            perror("rt_sigpending failed");
            return 1;
        }

        if (sigismember(&pending_set, SIGINT)) {
            printf("Child: SIGINT is pending.\\n");
        } else {
            printf("Child: SIGINT is NOT pending.\\n");
        }

        printf("Child process completed.\\n");
        return 0;
    } else {
        close(pipefd[1]);

        char buf;
        read(pipefd[0], &buf, 1);
        close(pipefd[0]);

        printf("Parent sending SIGINT to child (PID: %d)\\n", child_pid);
        if (kill(child_pid, SIGINT) == -1) {
            perror("kill failed");
            return 1;
        }

        kill(child_pid, SIGTERM);
        waitpid(child_pid, NULL, 0);
        printf("Child process terminated.\\n");
    }

    return 0;
}
"""

directory = "./tool/cfiles/127_rt_sigpending"
os.makedirs(directory, exist_ok=True)

filename = os.path.join(directory, "rt_sigpending_0.c")

with open(filename, "w") as f:
    f.write(template)

