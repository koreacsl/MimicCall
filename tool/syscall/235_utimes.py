# -*- coding: utf-8 -*-
import os

def generate_utimes_test():
    output_dir = "./tool/cfiles/utimes"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/time.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_utimes
#define SYS_utimes 235
#endif

int main() {
    const char *path = "/tmp/testfile_utimes";
    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        return 1;
    }
    close(fd);

    // Using NULL for the timesval array sets access and modification times to the current time.
    if (syscall(SYS_utimes, path, NULL) == -1) {
        unlink(path);
        return 1;
    }

    unlink(path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "utimes_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_utimes_test()
