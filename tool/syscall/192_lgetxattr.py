
import os

def generate_lgetxattr_tests():
    output_dir = "./tool/cfiles/192_lgetxattr"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/xattr.h>

#ifndef SYS_lgetxattr
#define SYS_lgetxattr 192
#endif

int main() {
    const char *target_path = "/tmp/test_lgetxattr_target";
    const char *symlink_path = "/tmp/test_lgetxattr_symlink";
    const char *name = "user.test";
    const char *value = "test_value";
    char buffer[32];

    int fd = open(target_path, O_CREAT, 0644);
    if (fd == -1) return 1;
    close(fd);
    symlink(target_path, symlink_path);
    lsetxattr(symlink_path, name, value, sizeof(value), 0);

    syscall(SYS_lgetxattr, symlink_path, name, buffer, sizeof(buffer));
    
    unlink(target_path);
    unlink(symlink_path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "lgetxattr_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_lgetxattr_tests()
