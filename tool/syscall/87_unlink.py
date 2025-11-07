
import os

def generate_unlink_tests():
    output_dir = "./tool/cfiles/87_unlink"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_unlink
#define SYS_unlink 87
#endif

int main() {
    const char* path = "/tmp/unlink_test_file";

    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        return 1;
    }
    close(fd);

    if (syscall(SYS_unlink, path) == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "unlink_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_unlink_tests()
