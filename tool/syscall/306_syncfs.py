import os

def generate_syncfs_tests():
    output_dir = "./tool/cfiles/306_syncfs"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_syncfs
#define SYS_syncfs 306
#endif

int main() {
    int fd = open("/dev/null", O_RDONLY);
    if (fd == -1) {
        return 1;
    }

    int result = syscall(SYS_syncfs, fd);

    close(fd);

    return (result == -1) ? 1 : 0;
}
"""
    filename = os.path.join(output_dir, "syncfs_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_syncfs_tests()