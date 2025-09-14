import os

def generate_writev_test():
    output_dir = "./tool/cfiles/1_write"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <fcntl.h>
#include <unistd.h>
#include <sys/uio.h>
#include <sys/syscall.h>
#include <linux/fs.h>

int main() {
    int fd = open("/dev/null", O_WRONLY | O_CREAT, 0644);
    if (fd == -1) return 1;

    char buf1[64] = "1";
    char buf2[64] = "2";
    struct iovec iov[2] = {
        {buf1, sizeof(buf1)},
        {buf2, sizeof(buf2)}
    };

    if (syscall(SYS_write, fd, iov, 2) == -1) {
        close(fd);
        return 1;
    }

    close(fd);
    return 0;
}
"""
    filename = f"{output_dir}/write_0.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_writev_test()