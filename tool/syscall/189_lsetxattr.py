
import os

def generate_lsetxattr_tests():
    output_dir = "./tool/cfiles/189_lsetxattr"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_lsetxattr
#define SYS_lsetxattr 189
#endif

int main() {
    const char *target_path = "/tmp/test_lsetxattr_target";
    const char *symlink_path = "/tmp/test_lsetxattr_symlink";
    const char *name = "user.test";
    const char *value = "test_value";

    int fd = open(target_path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) return 1;
    close(fd);

    if (symlink(target_path, symlink_path) != 0) {
        unlink(target_path);
        return 1;
    }

    syscall(SYS_lsetxattr, symlink_path, name, value, sizeof(value), 0);
    
    unlink(target_path);
    unlink(symlink_path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "lsetxattr_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_lsetxattr_tests()
