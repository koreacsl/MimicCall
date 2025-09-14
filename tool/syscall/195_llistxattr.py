# -*- coding: utf-8 -*-
import os

def generate_llistxattr_tests():
    output_dir = "./tool/cfiles/195_llistxattr"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/xattr.h>

#ifndef SYS_llistxattr
#define SYS_llistxattr 195
#endif

int main() {
    const char *target_path = "/tmp/test_llistxattr_target";
    const char *symlink_path = "/tmp/test_llistxattr_symlink";
    char buffer[128];

    int fd = open(target_path, O_CREAT, 0644);
    if (fd == -1) return 1;
    close(fd);
    symlink(target_path, symlink_path);
    lsetxattr(symlink_path, "user.test1", "v1", 2, 0);

    syscall(SYS_llistxattr, symlink_path, buffer, sizeof(buffer));
    
    unlink(target_path);
    unlink(symlink_path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "llistxattr_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_llistxattr_tests()
