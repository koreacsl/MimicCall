import os

def generate_rt_sigtimedwait_tests():
    output_dir = "./tool/cfiles/128_rt_sigtimedwait"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <signal.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>

#ifndef SYS_rt_sigprocmask
#define SYS_rt_sigprocmask 14
#endif

#ifndef SYS_rt_sigtimedwait
#define SYS_rt_sigtimedwait 128
#endif

#ifndef KERNEL_SIGSET_BYTES
#define KERNEL_SIGSET_BYTES 8
#endif

int main() {
    sigset_t set;
    sigemptyset(&set);
    sigaddset(&set, SIGUSR1);

    if (syscall(SYS_rt_sigprocmask, SIG_BLOCK, &set, NULL, KERNEL_SIGSET_BYTES) == -1) {
        perror("rt_sigprocmask");
        return 1;
    }

    if (kill(getpid(), SIGUSR1) == -1) {
        perror("kill");
        return 1;
    }

    struct timespec ts = { .tv_sec = 1, .tv_nsec = 0 };
    siginfo_t si;
    long r = syscall(SYS_rt_sigtimedwait, &set, &si, &ts, KERNEL_SIGSET_BYTES);
    if (r == -1) {
        perror("rt_sigtimedwait");
        return 1;
    }

    return 0;
}
"""
    filename = f"{output_dir}/rt_sigtimedwait_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_rt_sigtimedwait_tests()
