
import os

def generate_lremovexattr_tests():
    output_dir = "./tool/cfiles/198_lremovexattr"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/xattr.h>

#ifndef SYS_lremovexattr
#define SYS_lremovexattr 198
#endif

int main() {
    const char *target_path = "/tmp/test_lremovexattr_target";
    const char *symlink_path = "/tmp/test_lremovexattr_symlink";
    const char *name = "user.test";

    int fd = open(target_path, O_CREAT, 0644);
    if (fd == -1) return 1;
    close(fd);

    if (symlink(target_path, symlink_path) != 0) {
        unlink(target_path);
        return 1;
    }

    lsetxattr(symlink_path, name, "v", 1, 0);

    syscall(SYS_lremovexattr, symlink_path, name);
    
    unlink(target_path);
    unlink(symlink_path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "lremovexattr_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_lremovexattr_tests()