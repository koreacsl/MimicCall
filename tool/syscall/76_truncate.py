import os

def generate_truncate_tests():
    output_dir = "./tool/cfiles/76_truncate"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_truncate
#define SYS_truncate 76
#endif

int main() {
    const char *pathname = "./testfile_truncate";

    int fd = open(pathname, O_WRONLY | O_CREAT, 0644);
    if (fd == -1) {
        return 1;
    }
    close(fd);

    int result = syscall(SYS_truncate, pathname, 1024);

    unlink(pathname);

    return (result == -1) ? 1 : 0;
}
"""
    filename = os.path.join(output_dir, "truncate_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_truncate_tests()
