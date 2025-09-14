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

int main() {
    sigset_t mask;
    struct timespec timeout;

    sigemptyset(&mask);
    sigaddset(&mask, SIGUSR1);

    if (syscall(SYS_rt_sigprocmask, SIG_BLOCK, &mask, NULL, sizeof(mask)) == -1) {
        return 1;
    }

    timeout.tv_sec = 0;
    timeout.tv_nsec = 1;

    int result = syscall(SYS_rt_sigtimedwait, &mask, NULL, &timeout, sizeof(mask));

    if (result == -1 && errno == EAGAIN) {
        return 0;
    }

    return 1;
}
"""
    filename = f"{output_dir}/rt_sigtimedwait_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_rt_sigtimedwait_tests()
