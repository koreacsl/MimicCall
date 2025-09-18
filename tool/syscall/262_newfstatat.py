import os

def generate_newfstatat_tests():
    output_dir = "./tool/cfiles/262_newfstatat"
    os.makedirs(output_dir, exist_ok=True)

    flags = [
        "0",
        "AT_SYMLINK_NOFOLLOW",
        "AT_SYMLINK_FOLLOW",
        "AT_NO_AUTOMOUNT",
        "AT_EMPTY_PATH",
        "AT_STATX_SYNC_TYPE",
        "AT_STATX_SYNC_AS_STAT",
        "AT_STATX_FORCE_SYNC",
        "AT_STATX_DONT_SYNC"
    ]

    for flag in flags:
        c_code = f"""#define _GNU_SOURCE
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <linux/stat.h>
#include <string.h>
#include <stdlib.h>
#include <sys/syscall.h>

#ifndef SYS_newfstatat
#define SYS_newfstatat 262
#endif

#ifndef AT_SYMLINK_FOLLOW
#define AT_SYMLINK_FOLLOW 0x400
#endif
#ifndef AT_NO_AUTOMOUNT
#define AT_NO_AUTOMOUNT 0x800
#endif
#ifndef AT_EMPTY_PATH
#define AT_EMPTY_PATH 0x1000
#endif

int main() {{
    struct stat statbuf;
    int result = 0;

    int current_flags = {flag};

    if (current_flags & AT_EMPTY_PATH) {{
        int fd = open("/dev/null", O_PATH | O_CLOEXEC);
        if (fd == -1) return 1;
        result = syscall(SYS_newfstatat, AT_FDCWD, "/dev/null", &statbuf, current_flags);
    }}
    
    if (result == -1) {{
        return 1;
    }}

    return 0;
}}
"""
        filename = f"{output_dir}/newfstatat_{flag.lower()}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_newfstatat_tests()

