import os
import sys

def generate_statfs_test():
    output_dir = "./tool/cfiles/137_statfs"
    os.makedirs(output_dir, exist_ok=True)
        
    c_code = """#include <sys/vfs.h>
#include <sys/statfs.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_statfs
#  define SYS_statfs 137
#endif

int main() {
    struct statfs buf;
    if (syscall(SYS_statfs, "/dev/null", &buf) == -1) {
        return 1;
    }
    return 0;
}
"""
    filename = f"{output_dir}/statfs_0.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_statfs_test()
