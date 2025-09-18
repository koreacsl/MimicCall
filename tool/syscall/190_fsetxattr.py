
import os

def generate_fsetxattr_tests():
    output_dir = "./tool/cfiles/190_fsetxattr"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_fsetxattr
#define SYS_fsetxattr 190
#endif

int main() {
    const char *path = "/tmp/test_fsetxattr_file";
    const char *name = "user.test";
    const char *value = "test_value";

    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) return 1;

    syscall(SYS_fsetxattr, fd, name, value, sizeof(value), 0);
    
    close(fd);
    unlink(path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "fsetxattr_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_fsetxattr_tests()
