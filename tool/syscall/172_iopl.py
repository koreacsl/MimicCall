import os

template = """#define _GNU_SOURCE
#include <sys/io.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>

int main() {
    int level = {iopl_level};

    int result = syscall(SYS_iopl, level);
    if (result == -1) {
        perror("iopl failed");
        return 1;
    }

    if (level > 0) {
        syscall(SYS_iopl, 0);
    }

    return 0;
}
"""

directory = "./tool/cfiles/172_iopl"
os.makedirs(directory, exist_ok=True)

iopl_levels = ["0", "1", "2", "3"]

for level in iopl_levels:
    filename = os.path.join(directory, f"iopl_{level}.c")
    with open(filename, "w") as f:
        f.write(template.replace("{iopl_level}", level))
