
import os

def generate_utime_test():
    output_dir = "./tool/cfiles/132_utime"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/types.h>
#include <utime.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_utime
#define SYS_utime 132
#endif

int main() {
    const char *path = "/tmp/testfile_utime";
    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        return 1;
    }
    close(fd);

    if (syscall(SYS_utime, path, NULL) == -1) {
        unlink(path);
        return 1;
    }

    unlink(path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "utime_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_utime_test()
