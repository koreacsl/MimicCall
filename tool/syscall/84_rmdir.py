# -*- coding: utf-8 -*-
import os

def generate_rmdir_test():
    output_dir = "./tool/cfiles/84_rmdir"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/stat.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_rmdir
#define SYS_rmdir 84
#endif

#ifndef SYS_mkdir
#define SYS_mkdir 83
#endif

int main() {
    const char* path = "/tmp/test_rmdir_dir";

    rmdir(path);

    if (syscall(SYS_mkdir, path, 0755) == -1) {
        return 1;
    }

    if (syscall(SYS_rmdir, path) == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "rmdir_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_rmdir_test()
