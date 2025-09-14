import os

output_dir = "./tool/cfiles/427_io_uring_register"
os.makedirs(output_dir, exist_ok=True)

opcodes = {
        "IORING_REGISTER_BUFFERS": {
        "define": 0,
        "prepare": '''
    char buf[8] = "abcd";
    struct iovec vec = {
        .iov_base = buf,
        .iov_len = sizeof(buf)
    };
''',
        "arg": "&vec",
        "nr_args": "1"
    },
    "IORING_UNREGISTER_BUFFERS": {
        "define": 1,
        "prepare": '',
        "arg": "0",
        "nr_args": "0"
    },
    "IORING_REGISTER_FILES": {
        "define": 2,
        "prepare": '''
    int fd = open("/dev/null", O_RDONLY);
    if (fd < 0) return 1;
''',
        "arg": "&fd",
        "nr_args": "1"
    },
    "IORING_UNREGISTER_FILES": {
        "define": 3,
        "prepare": '',
        "arg": "0",
        "nr_args": "0"
    },
    "IORING_REGISTER_EVENTFD": {
        "define": 4,
        "prepare": '''
    int efd = eventfd(0, 0);
    if (efd < 0) return 1;
''',
        "arg": "&efd",
        "nr_args": "1"
    },
    "IORING_UNREGISTER_EVENTFD": {
        "define": 5,
        "prepare": '',
        "arg": "0",
        "nr_args": "0"
    },
    "IORING_REGISTER_FILES_UPDATE": {
        "define": 6,
        "prepare": '''
    int fd = open("/dev/null", O_RDONLY);
    if (fd < 0) return 1;
    struct io_uring_files_update upd = {
        .offset = 0,
        .resv = 0,
        .fds = &fd
    };
''',
        "arg": "&upd",
        "nr_args": "1"
    },
    "IORING_REGISTER_EVENTFD_ASYNC": {
        "define": 7,
        "prepare": '''
    int efd = eventfd(0, 0);
    if (efd < 0) return 1;
''',
        "arg": "&efd",
        "nr_args": "1"
    },
    "IORING_REGISTER_PROBE": {
        "define": 8,
        "prepare": '''
    struct io_uring_probe probe;
    memset(&probe, 0, sizeof(probe));
''',
        "arg": "&probe",
        "nr_args": "1"
    },
    "IORING_REGISTER_PERSONALITY": {
        "define": 9,
        "prepare": '',
        "arg": "0",
        "nr_args": "0"
    },
    "IORING_UNREGISTER_PERSONALITY": {
        "define": 10,
        "prepare": '',
        "arg": "0",
        "nr_args": "1"
    },
    "IORING_REGISTER_FILES2": {
        "define": 13,
        "prepare": '''
    int temp_fd = open("/dev/null", O_RDONLY);
    if (temp_fd < 0) return 1;
    struct io_uring_rsrc_register reg = {
        .nr = 1,
        .flags = 0,
        .resv2 = 0,
        .data = (void*)&temp_fd,
        .tags = 0,
    };
''',
        "arg": "&reg",
        "nr_args": "sizeof(reg)"
    },
    "IORING_REGISTER_BUFFERS2": {
        "define": 15,
        "prepare": '''
    char buffer[8] = "test";
    struct iovec vec = {
        .iov_base = buffer,
        .iov_len = sizeof(buffer)
    };
    struct io_uring_rsrc_register reg = {
        .nr = 1,
        .flags = 0,
        .resv2 = 0,
        .data = (void*)&vec,
        .tags = 0
    };
''',
        "arg": "&reg",
        "nr_args": "sizeof(reg)"
    },
    "IORING_REGISTER_BUFFERS_UPDATE": {
        "define": 16,
        "prepare": '''
    char buffer[8] = "test";
    struct iovec vec = {
        .iov_base = buffer,
        .iov_len = sizeof(buffer)
    };
    struct io_uring_rsrc_update2 upd = {
        .offset = 0,
        .resv = 0,
        .data = (void*)&vec,
        .tags = 0,
        .nr = 1,
        .resv2 = 0
    };
''',
        "arg": "&upd",
        "nr_args": "sizeof(upd)"
    },
    "IORING_REGISTER_FILES_UPDATE2": {
        "define": 14,
        "prepare": '''
    int temp_fd = open("/dev/null", O_RDONLY);
    if (temp_fd < 0) return 1;
    struct io_uring_rsrc_update2 upd = {
        .offset = 0,
        .resv = 0,
        .data = (void*)&temp_fd,
        .tags = 0,
        .nr = 1,
        .resv2 = 0
    };
''',
        "arg": "&upd",
        "nr_args": "sizeof(upd)"
    },
    "IORING_REGISTER_RESTRICTIONS": {
        "define": 11,
        "prepare": '''
    struct io_uring_restriction rest = {
        .opcode = IORING_RESTRICTION_REGISTER_OP,
        .oparg = IORING_REGISTER_FILES,
        .resv = 0,
        .resv2 = {0, 0, 0}
    };
''',
        "arg": "&rest",
        "nr_args": "1"
    }
}

common_header = '''\
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <linux/io_uring.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <sys/eventfd.h>
#include <sys/uio.h>

#ifndef SYS_io_uring_setup
#define SYS_io_uring_setup 425
#endif
#ifndef SYS_io_uring_register
#define SYS_io_uring_register 427
#endif
'''

def write_test(opcode, info):
    name = f"io_uring_register_{opcode.lower()}"
    define_val = info["define"]
    prepare_code = info["prepare"]
    arg = info["arg"]
    nr_args = info["nr_args"]

    content = f"""{common_header}
#ifndef {opcode}
#define {opcode} {define_val}
#endif

#ifndef IORING_RESTRICTION_REGISTER_OP
#define IORING_RESTRICTION_REGISTER_OP 0
#endif
#ifndef IORING_REGISTER_FILES
#define IORING_REGISTER_FILES 2
#endif

int main() {{
    struct io_uring_params p;
    memset(&p, 0, sizeof(p));
    int ring_fd = syscall(SYS_io_uring_setup, 1, &p);
    if (ring_fd < 0) {{
        perror("io_uring_setup");
        return 1;
    }}

{prepare_code.strip()}

    int ret = syscall(SYS_io_uring_register, ring_fd, {opcode}, {arg}, {nr_args});
    if (ret < 0) {{
        perror("io_uring_register failed");
        close(ring_fd);
        return 1;
    }}

    close(ring_fd);
    return 0;
}}
"""
    with open(os.path.join(output_dir, f"{name}.c"), "w") as f:
        f.write(content)

for opcode, info in opcodes.items():
    write_test(opcode, info)
