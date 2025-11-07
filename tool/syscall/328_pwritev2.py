import os

def generate_pwritev2_tests():
    output_dir = "./tool/cfiles/328_pwritev2"
    os.makedirs(output_dir, exist_ok=True)

    rwf_flags = ["RWF_DSYNC", "RWF_HIPRI", "RWF_SYNC", "RWF_NOWAIT", "RWF_APPEND"]

    for flag in rwf_flags:
        c_code = f"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <sys/uio.h>
#include <sys/syscall.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

#ifndef SYS_pwritev2
#define SYS_pwritev2 328
#endif

#ifndef RWF_HIPRI
#define RWF_HIPRI   0x00000001
#endif
#ifndef RWF_DSYNC
#define RWF_DSYNC   0x00000002
#endif
#ifndef RWF_SYNC
#define RWF_SYNC    0x00000004
#endif
#ifndef RWF_NOWAIT
#define RWF_NOWAIT  0x00000008
#endif
#ifndef RWF_APPEND
#define RWF_APPEND  0x00000010
#endif

#ifndef EXIT_SKIP
#define EXIT_SKIP 0
#endif

int main(void) {{
    char path[] = "/tmp/pwritev2_test_XXXXXX";
    int fd = mkstemp(path);
    if (fd == -1) {{
        perror("mkstemp");
        return 1;
    }}
    unlink(path);

    if (write(fd, "seed", 4) != 4) {{
        perror("write(seed)");
        close(fd);
        return 1;
    }}

    char buf1[64]; memset(buf1, 0, sizeof buf1); buf1[0] = '1';
    char buf2[64]; memset(buf2, 0, sizeof buf2); buf2[0] = '2';
    struct iovec iov[2] = {{
        {{ .iov_base = buf1, .iov_len = sizeof buf1 }},
        {{ .iov_base = buf2, .iov_len = sizeof buf2 }},
    }};

    off_t off = ({flag} == RWF_APPEND) ? (off_t)-1 : (off_t)0;

    ssize_t ret = syscall(SYS_pwritev2, fd, iov, 2, off, {flag});
    if (ret == -1) {{
        if (errno == EOPNOTSUPP || errno == EINVAL) {{
            close(fd);
            return EXIT_SKIP;
        }}
        perror("pwritev2");
        close(fd);
        return 1;
    }}

    close(fd);
    return 0;
}}
"""
        filename = f"{output_dir}/test_{flag.lower()}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_pwritev2_tests()
