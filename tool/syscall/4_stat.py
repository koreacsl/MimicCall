import os

def generate_stat_test():
    output_dir = "./tool/cfiles/4_stat"
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

#ifndef SYS_stat
#define SYS_stat 4
#endif

int main() {
    struct stat statbuf;
    if (syscall(SYS_stat, "/dev/null", &statbuf) == -1) {
        return 1;
    }
    return 0;
}
"""
    filename = f"{output_dir}/test_stat.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_stat_test()
