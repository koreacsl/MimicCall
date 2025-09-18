import os

def generate_signalfd4_tests():
    output_dir = "./tool/cfiles/289_signalfd4"
    os.makedirs(output_dir, exist_ok=True)

    signalfd4_flags = {
        "none": "0",
        "nonblock": "SFD_NONBLOCK",
        "cloexec": "SFD_CLOEXEC"
    }

    for flag_name, flag_value in signalfd4_flags.items():
        c_code = f"""#include <signal.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/signalfd.h>

#define KERNEL_SIGSET_BYTES 8

#ifndef SYS_signalfd4
#define SYS_signalfd4 289
#endif

#ifndef SYS_rt_sigprocmask
#define SYS_rt_sigprocmask 14
#endif

#ifndef SYS_kill
#define SYS_kill 62
#endif

int main() {{
    sigset_t mask;
    int sfd;
    struct signalfd_siginfo fdsi;

    sigemptyset(&mask);
    sigaddset(&mask, SIGUSR1);

    if (syscall(SYS_rt_sigprocmask, SIG_BLOCK, &mask, NULL, KERNEL_SIGSET_BYTES) == -1) {{
        return 1;
    }}

    sfd = syscall(SYS_signalfd4, -1, &mask, KERNEL_SIGSET_BYTES, {flag_value});
    if (sfd == -1) {{
        return 1;
    }}

    syscall(SYS_kill, getpid(), SIGUSR1);

    if (read(sfd, &fdsi, sizeof(struct signalfd_siginfo)) != sizeof(struct signalfd_siginfo)) {{
        close(sfd);
        return 1;
    }}

    close(sfd);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"signalfd4_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_signalfd4_tests()
