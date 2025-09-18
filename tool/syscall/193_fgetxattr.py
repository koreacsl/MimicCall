
import os

def generate_fgetxattr_tests():
    output_dir = "./tool/cfiles/193_fgetxattr"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/xattr.h>

#ifndef SYS_fgetxattr
#define SYS_fgetxattr 193
#endif

int main() {
    const char *path = "/tmp/test_fgetxattr_file";
    const char *name = "user.test";
    const char *value = "test_value";
    char buffer[32];

    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) return 1;
    fsetxattr(fd, name, value, sizeof(value), 0);

    syscall(SYS_fgetxattr, fd, name, buffer, sizeof(buffer));
    
    close(fd);
    unlink(path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "fgetxattr_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_fgetxattr_tests()
