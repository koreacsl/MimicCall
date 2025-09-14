import os

def generate_pwritev2_tests():
    output_dir = "./tool/cfiles/328_pwritev2"
    os.makedirs(output_dir, exist_ok=True)

    rwf_flags = [
        "RWF_DSYNC",
        "RWF_HIPRI",
        "RWF_SYNC",
        "RWF_NOWAIT",
        "RWF_APPEND"
    ]
    
    for flag in rwf_flags:
        c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/uio.h>
#include <sys/syscall.h>
#include <linux/fs.h>

#ifndef {flag}
#define {flag} 0x00000001
#endif

int main() {{
    int fd = open("/dev/null", O_WRONLY | O_CREAT, 0644);
    if (fd == -1) return 1;

    char buf1[64] = "1";
    char buf2[64] = "2";
    struct iovec iov[2] = {{
        {{buf1, sizeof(buf1)}},
        {{buf2, sizeof(buf2)}}
    }};

    ssize_t result;

    result = syscall(SYS_pwritev2, fd, iov, 2, 0, {flag});

    close(fd);
    return (result >= 0) ? 0 : 1;
}}
"""
        filename = f"{output_dir}/test_{flag.lower()}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_pwritev2_tests()

