
import os

def generate_setxattr_tests():
    output_dir = "./tool/cfiles/188_setxattr"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_setxattr
#define SYS_setxattr 188
#endif

int main() {
    const char *path = "/tmp/test_setxattr_file";
    const char *name = "user.test";
    const char *value = "test_value";

    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) return 1;
    close(fd);

    syscall(SYS_setxattr, path, name, value, sizeof(value), 0);
    
    unlink(path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "setxattr_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_setxattr_tests()
