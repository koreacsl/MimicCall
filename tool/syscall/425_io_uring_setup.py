import os

output_dir = "./tool/cfiles/425_io_uring_setup"
os.makedirs(output_dir, exist_ok=True)

uring_flags = [
    "0", "IORING_SETUP_IOPOLL", "IORING_SETUP_SQPOLL", "IORING_SETUP_SQ_AFF",
    "IORING_SETUP_CQSIZE", "IORING_SETUP_CLAMP", "IORING_SETUP_ATTACH_WQ",
    "IORING_FEAT_NODROP", "IORING_FEAT_SUBMIT_STABLE", "IORING_FEAT_RW_CUR_POS",
    "IORING_FEAT_FAST_POLL", "IORING_FEAT_POLL_32BITS", "IORING_SETUP_R_DISABLED",
    "IORING_FEAT_SQPOLL_NONFIXED", "IORING_FEAT_NATIVE_WORKERS", "IORING_FEAT_RSRC_TAGS",
    "IORING_FEAT_CQE_SKIP", "IORING_SETUP_SUBMIT_ALL", "IORING_SETUP_COOP_TASKRUN",
    "IORING_SETUP_TASKRUN_FLAG", "IORING_SETUP_SQE128", "IORING_SETUP_CQE32",
    "IORING_SETUP_SINGLE_ISSUER", "IORING_SETUP_DEFER_TASKRUN"
]

common_headers = """\
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <linux/io_uring.h>
#include <stdint.h>
#include <string.h>

#ifndef SYS_io_uring_setup
#define SYS_io_uring_setup 425
#endif
"""

def write_c_file(name, content):
    with open(os.path.join(output_dir, f"{name}.c"), "w") as f:
        f.write(content)

def generate_uring_setup_tests():
    for flag in uring_flags:
        name = f"io_uring_setup_flag_{flag.lower()}"
        content = f"""{common_headers}
int main() {{
    struct io_uring_params p;
    memset(&p, 0, sizeof(p));
    p.flags = {flag};
    int fd = syscall(SYS_io_uring_setup, 1, &p);
    if (fd >= 0) close(fd);
    return 0;
}}
"""
        write_c_file(name, content)

generate_uring_setup_tests()
