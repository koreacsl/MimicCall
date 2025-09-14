# -*- coding: utf-8 -*-
import os

def generate_readlink_tests():
    output_dir = "./tool/cfiles/89_readlink"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_readlink
#define SYS_readlink 89
#endif

int main() {
    const char* target = "/tmp/readlink_test_target";
    const char* linkpath = "/tmp/readlink_test_link";
    char buf[1024];

    unlink(target);
    unlink(linkpath);

    int fd = open(target, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        return 1;
    }
    close(fd);

    if (symlink(target, linkpath) == -1) {
        unlink(target);
        return 1;
    }

    if (syscall(SYS_readlink, linkpath, buf, sizeof(buf) - 1) == -1) {
        unlink(target);
        unlink(linkpath);
        return 1;
    }
    
    unlink(target);
    unlink(linkpath);

    return 0;
}
"""
    filename = os.path.join(output_dir, "readlink_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_readlink_tests()
