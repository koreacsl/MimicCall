import os

def generate_ftruncate_tests():
    output_dir = "./tool/cfiles/77_ftruncate"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_ftruncate
#define SYS_ftruncate 77
#endif

int main() {
    const char *pathname = "./testfile_ftruncate";

    int fd = open(pathname, O_RDWR | O_CREAT, 0644);
    if (fd == -1) {
        return 1;
    }

    int result = syscall(SYS_ftruncate, fd, 1024);

    close(fd);

    unlink(pathname);

    return (result == -1) ? 1 : 0;
}
"""
    filename = os.path.join(output_dir, "ftruncate_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_ftruncate_tests()
