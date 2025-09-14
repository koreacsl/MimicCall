# -*- coding: utf-8 -*-
import os

def generate_mount_tests():
    output_dir = "./tool/cfiles/mount"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/mount.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/stat.h>
#include <fcntl.h>

#ifndef SYS_mount
#define SYS_mount 165
#endif
#ifndef SYS_umount2
#define SYS_umount2 166
#endif

int main() {
    const char *src = "/tmp/mount_src_root";
    const char *tgt = "/tmp/mount_tgt_root";
    int mount_result = -1;
    int umount_result = -1;

    rmdir(src);
    rmdir(tgt);

    if (mkdir(src, 0755) != 0 || mkdir(tgt, 0755) != 0) {
        return 1;
    }

    mount_result = syscall(SYS_mount, "tmpfs", tgt, "tmpfs", 0, NULL);
    if (mount_result != 0) {
        rmdir(src);
        rmdir(tgt);
        return 1;
    }

    umount_result = syscall(SYS_umount2, tgt, 0);

    rmdir(src);
    rmdir(tgt);

    if (mount_result == 0 && umount_result == 0) {
        return 0;
    }

    return 1;
}
"""
    filename = os.path.join(output_dir, "mount_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_mount_tests()

