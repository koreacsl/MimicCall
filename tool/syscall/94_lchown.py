# -*- coding: utf-8 -*-
import os

def generate_lchown_tests():
    output_dir = "./tool/cfiles/94_lchown"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_lchown
#define SYS_lchown 94
#endif

int main() {
    const char* target_path = "/tmp/lchown_test_target";
    const char* link_path = "/tmp/lchown_test_link";
    uid_t uid = getuid();
    gid_t gid = getgid();

    unlink(target_path);
    unlink(link_path);

    int fd = open(target_path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        return 1;
    }
    close(fd);

    if (symlink(target_path, link_path) == -1) {
        unlink(target_path);
        return 1;
    }

    if (syscall(SYS_lchown, link_path, uid, gid) == -1) {
        unlink(target_path);
        unlink(link_path);
        return 1;
    }

    unlink(target_path);
    unlink(link_path);

    return 0;
}
"""
    filename = os.path.join(output_dir, "lchown_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_lchown_tests()
