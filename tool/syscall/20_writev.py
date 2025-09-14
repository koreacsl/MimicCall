import os

def generate_writev_tests():
    output_dir = "./tool/cfiles/20_writev"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <fcntl.h>
#include <unistd.h>
#include <sys/uio.h>
#include <sys/syscall.h>
#include <string.h>

#ifndef SYS_writev
#define SYS_writev 20
#endif

int main() {
    int fd = open("/dev/null", O_WRONLY);
    if (fd == -1) {
        return 1;
    }

    char buf1[] = "1";
    char buf2[] = "2";
    
    struct iovec iov[2] = {
        { .iov_base = buf1, .iov_len = strlen(buf1) },
        { .iov_base = buf2, .iov_len = strlen(buf2) }
    };

    ssize_t result = syscall(SYS_writev, fd, iov, 2);

    close(fd);

    if (result == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = f"{output_dir}/writev_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_writev_tests()
