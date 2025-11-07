
import os

def generate_rt_sigqueueinfo_test():
    output_dir = "./tool/cfiles/129_rt_sigqueueinfo"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
#include <signal.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <stdlib.h>

#ifndef SYS_rt_sigqueueinfo
#define SYS_rt_sigqueueinfo 127
#endif

void signal_handler(int sig) {
    _exit(0);
}

int main() {
    int pipefd[2];
    if (pipe(pipefd) == -1) {
        return 1;
    }

    pid_t child_pid = fork();
    if (child_pid == -1) {
        return 1;
    }

    if (child_pid == 0) {
        close(pipefd[0]);
        struct sigaction sa;
        memset(&sa, 0, sizeof(sa));
        sa.sa_handler = signal_handler;
        if (sigaction(SIGUSR1, &sa, NULL) == -1) {
            _exit(1);
        }
        write(pipefd[1], "R", 1);
        close(pipefd[1]);
        pause();
        _exit(1);
    } else {
        close(pipefd[1]);
        char buf;
        read(pipefd[0], &buf, 1);
        close(pipefd[0]);

        siginfo_t info;
        memset(&info, 0, sizeof(info));
        info.si_signo = SIGUSR1;
        info.si_code = SI_QUEUE;
        info.si_int = 1234;

        if (syscall(SYS_rt_sigqueueinfo, child_pid, SIGUSR1, &info) == -1) {
            kill(child_pid, SIGKILL);
            waitpid(child_pid, NULL, 0);
            return 1;
        }

        int status;
        waitpid(child_pid, &status, 0);

        if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
            return 0;
        }
    }

    return 1;
}
"""
    filename = os.path.join(output_dir, "rt_sigqueueinfo_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_rt_sigqueueinfo_test()

