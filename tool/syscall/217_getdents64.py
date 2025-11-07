import os

def generate_getdents64_test():
    output_dir = "./tool/cfiles/217_getdents64"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_getdents64
#define SYS_getdents64 217
#endif

int main() {
    int fd = open(".", O_RDONLY | O_DIRECTORY);
    if (fd == -1) {
        return 1;
    }

    char buffer[1024];
    int nread = syscall(SYS_getdents64, fd, buffer, sizeof(buffer));

    close(fd);

    return nread == -1 ? 1 : 0;
}
"""
    filename = os.path.join(output_dir, "getdents64_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_getdents64_test()
