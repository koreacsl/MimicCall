import os

def generate_kcmp_tests():
    output_dir = "./tool/cfiles/312_kcmp"

    kcmp_flags = [
        ("kcmp_file", "KCMP_FILE"),
        ("kcmp_files", "KCMP_FILES"),
        ("kcmp_fs", "KCMP_FS"),
        ("kcmp_io", "KCMP_IO"),
        ("kcmp_sighand", "KCMP_SIGHAND"),
        ("kcmp_sysvsem", "KCMP_SYSVSEM"),
        ("kcmp_vm", "KCMP_VM")
    ]

    for syscall_name, flag in kcmp_flags:
        c_code = f"""#define _GNU_SOURCE
#include <linux/kcmp.h>
#include <sys/syscall.h>
#include <unistd.h>

int main() {{
    pid_t pid = getpid();
    int result = syscall(SYS_kcmp, pid, pid, {flag}, 0, 0);
    return result == -1 ? 1 : 0;
}}
"""
        filename = f"{output_dir}/{syscall_name}.c"
        with open(filename, "w") as f:
            f.write(c_code)

    syscall_name = "kcmp_epoll_tfd"
    c_code = f"""#define _GNU_SOURCE
#include <linux/kcmp.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <sys/epoll.h>

int main() {{
    pid_t pid = getpid();
    int efd = epoll_create1(0);
    int fd = 1;

    struct kcmp_epoll_slot slot = {{
        .efd = efd,
        .tfd = fd,
        .toff = 0
    }};

    int result = syscall(SYS_kcmp, pid, pid, KCMP_EPOLL_TFD, fd, (unsigned long)&slot);
    
    close(efd);
    return result == -1 ? 1 : 0;
}}
"""
    filename = f"{output_dir}/{syscall_name}.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    output_dir = "./tool/cfiles/312_kcmp"
    os.makedirs(output_dir, exist_ok=True)
    generate_kcmp_tests()
