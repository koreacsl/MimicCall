# -*- coding: utf-8 -*-
import os

def generate_chown_tests():
    output_dir = "./tool/cfiles/92_chown"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_chown
#define SYS_chown 92
#endif

int main() {
    const char* path = "/tmp/chown_test_file";
    uid_t uid = getuid();
    gid_t gid = getgid();

    unlink(path);

    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        return 1;
    }
    close(fd);

    if (syscall(SYS_chown, path, uid, gid) == -1) {
        unlink(path);
        return 1;
    }

    if (unlink(path) == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "chown_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_chown_tests()
