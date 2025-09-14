import os
import sys

def generate_preadv2_tests():
    output_dir = "./tool/cfiles/327_preadv2"
    os.makedirs(output_dir, exist_ok=True)

    rwf_flags = [
        "RWF_DSYNC",
        "RWF_HIPRI",
        "RWF_SYNC",
        "RWF_NOWAIT",
    ]

    for flag in rwf_flags:
        c_code = """#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <sys/uio.h>
#include <sys/syscall.h>
#include <linux/fs.h>

#ifndef SYS_preadv2
#  define SYS_preadv2 327
#endif

#ifndef RWF_HIPRI
#define RWF_HIPRI 0x00000001
#endif
#ifndef RWF_DSYNC
#define RWF_DSYNC 0x00000002
#endif
#ifndef RWF_SYNC
#define RWF_SYNC 0x00000004
#endif
#ifndef RWF_NOWAIT
#define RWF_NOWAIT 0x00000008
#endif

int main() {{
    int fd = open("/dev/null", O_RDONLY);
    if (fd == -1) return 1;

    char buf1[64], buf2[64];
    struct iovec iov[2] = {{
        {{buf1, sizeof(buf1)}},
        {{buf2, sizeof(buf2)}}
    }};

    long result = syscall(SYS_preadv2, fd, iov, 2, 0, 0, {flag});

    close(fd);
    return (result >= 0) ? 0 : 1;
}}
"""
        c_code = c_code.format(flag=flag)
        filename = f"{output_dir}/preadv2_{flag.lower()}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_preadv2_tests()
