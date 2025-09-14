# -*- coding: utf-8 -*-
import os

def generate_listxattr_tests():
    output_dir = "./tool/cfiles/194_listxattr"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/xattr.h>

#ifndef SYS_listxattr
#define SYS_listxattr 194
#endif

int main() {
    const char *path = "/tmp/test_listxattr_file";
    char buffer[128];

    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) return 1;
    close(fd);
    setxattr(path, "user.test1", "v1", 2, 0);
    setxattr(path, "user.test2", "v2", 2, 0);

    syscall(SYS_listxattr, path, buffer, sizeof(buffer));
    
    unlink(path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "listxattr_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_listxattr_tests()
