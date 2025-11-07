import os

def generate_pwrite64_test():
    output_dir = "./tool/cfiles/18_pwrite64"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/fs.h>

int main() {
    int fd = open("/dev/null", O_WRONLY | O_CREAT, 0644);
    if (fd == -1) return 1;

    char buf[128] = "1";
    if (syscall(SYS_pwrite64, fd, buf, sizeof(buf), 0) == -1) {
        close(fd);
        return 1;
    }

    close(fd);
    return 0;
}
"""
    filename = f"{output_dir}/pwrite64_0.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_pwrite64_test()

