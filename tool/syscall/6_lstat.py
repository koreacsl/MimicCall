import os

def generate_lstat_test():
    output_dir = "./tool/cfiles/6_lstat"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <fcntl.h>
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <linux/stat.h>
#include <string.h>
#include <stdlib.h>
#include <sys/syscall.h>

#ifndef SYS_lstat
#define SYS_lstat 6
#endif

int main() {
    const char *linkpath = "./test_symlink_for_lstat";
    if (symlink("/dev/null", linkpath) == -1) {
        return 1;
    }

    struct stat statbuf;
    if (syscall(SYS_lstat, linkpath, &statbuf) == -1) {
        unlink(linkpath);
        return 1;
    }

    unlink(linkpath);
    return 0;
}
"""
    filename = f"{output_dir}/lstat_0.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_lstat_test()
