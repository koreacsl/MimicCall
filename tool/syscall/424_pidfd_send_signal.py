import os

def generate_pidfd_send_signal_test():
    output_dir = "./tool/cfiles/424_pidfd_send_signal"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <signal.h>

#ifndef SYS_pidfd_open
#define SYS_pidfd_open 434
#endif

#ifndef SYS_pidfd_send_signal
#define SYS_pidfd_send_signal 424
#endif

int main() {
    int pidfd = syscall(SYS_pidfd_open, getpid(), 0);
    if (pidfd == -1) {
        return 1;
    }
    
    int result = syscall(SYS_pidfd_send_signal, pidfd, SIGUSR1, NULL, 0);

    close(pidfd);

    if (result == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = f"{output_dir}/pidfd_send_signal_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_pidfd_send_signal_test()
