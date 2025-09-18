
import os

def generate_removexattr_tests():
    output_dir = "./tool/cfiles/197_removexattr"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/xattr.h>

#ifndef SYS_removexattr
#define SYS_removexattr 197
#endif

int main() {
    const char *path = "/tmp/test_removexattr_file";
    const char *name = "user.test";

    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) return 1;
    close(fd);
    setxattr(path, name, "v", 1, 0);

    syscall(SYS_removexattr, path, name);
    
    unlink(path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "removexattr_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_removexattr_tests()
