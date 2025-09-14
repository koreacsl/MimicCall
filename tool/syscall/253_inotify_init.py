# -*- coding: utf-8 -*-
import os

def generate_inotify_init_test():
    output_dir = "./tool/cfiles/253_inotify_init"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_inotify_init
#define SYS_inotify_init 253
#endif

int main() {
    int fd = syscall(SYS_inotify_init);
    if (fd == -1) {
        return 1;
    }
    close(fd);
    return 0;
}
"""
    filename = os.path.join(output_dir, "inotify_init.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_inotify_init_test()

