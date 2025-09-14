# -*- coding: utf-8 -*-
import os

def generate_getxattr_tests():
    output_dir = "./tool/cfiles/191_getxattr"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/xattr.h>

#ifndef SYS_getxattr
#define SYS_getxattr 191
#endif

int main() {
    const char *path = "/tmp/test_getxattr_file";
    const char *name = "user.test";
    const char *value = "test_value";
    char buffer[32];

    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) return 1;
    close(fd);
    setxattr(path, name, value, sizeof(value), 0);

    syscall(SYS_getxattr, path, name, buffer, sizeof(buffer));
    
    unlink(path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "getxattr_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_getxattr_tests()
