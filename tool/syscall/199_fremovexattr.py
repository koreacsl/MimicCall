
import os

def generate_fremovexattr_tests():
    output_dir = "./tool/cfiles/199_fremovexattr"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/xattr.h>

#ifndef SYS_fremovexattr
#define SYS_fremovexattr 199
#endif

int main() {
    const char *path = "/tmp/test_fremovexattr_file";
    const char *name = "user.test";

    int fd = open(path, O_CREAT | O_RDWR, 0644);
    if (fd == -1) return 1;
    
    fsetxattr(fd, name, "v", 1, 0);

    syscall(SYS_fremovexattr, fd, name);
    
    close(fd);
    unlink(path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "fremovexattr_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_fremovexattr_tests()