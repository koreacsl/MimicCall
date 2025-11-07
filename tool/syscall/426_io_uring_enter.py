import os

output_dir = "./tool/cfiles/426_io_uring_enter"
os.makedirs(output_dir, exist_ok=True)

enter_flags = [
    "IORING_ENTER_GETEVENTS", "IORING_ENTER_SQ_WAKEUP",
    "IORING_ENTER_SQ_WAIT", "IORING_ENTER_EXT_ARG", "IORING_ENTER_REGISTERED_RING"
]

flag_definitions = {
    "IORING_ENTER_GETEVENTS": 1,
    "IORING_ENTER_SQ_WAKEUP": 2,
    "IORING_ENTER_SQ_WAIT": 4,
    "IORING_ENTER_EXT_ARG": 8,
    "IORING_ENTER_REGISTERED_RING": 16,
    "IORING_ENTER_ABS_TIMER": 32,
    "IORING_ENTER_EXT_ARG_REG": 64,
}

flag_defines = "\n".join([
    f"#ifndef {flag}\n#define {flag} {value}\n#endif"
    for flag, value in flag_definitions.items()
])

common_headers = f"""\
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <linux/io_uring.h>
#include <stdint.h>
#include <string.h>
#include <signal.h>

#ifndef SYS_io_uring_setup
#define SYS_io_uring_setup 425
#endif
#ifndef SYS_io_uring_enter
#define SYS_io_uring_enter 426
#endif

{flag_defines}
"""

def write_c_file(name, content, base_dir):
    with open(os.path.join(base_dir, f"{name}.c"), "w") as f:
        f.write(content)

def generate_io_uring_enter_tests():
    for flag in enter_flags:
        name = f"io_uring_enter_flag_{flag.lower()}"
        content = f"""{common_headers}
int main() {{
    struct io_uring_params p;
    memset(&p, 0, sizeof(p));
    int fd = syscall(SYS_io_uring_setup, 1, &p);
    if (fd < 0) return 1;

    syscall(SYS_io_uring_enter, fd, 0, 0, {flag}, NULL, 0);
    close(fd);
    return 0;
}}
"""
        write_c_file(name, content, output_dir)

generate_io_uring_enter_tests()
