import os

template = """#define _GNU_SOURCE
#include <sys/sysinfo.h>
#include <stdio.h>
#include <errno.h>

int main() {
    struct sysinfo info;

    if (sysinfo(&info) == -1) {
        perror("sysinfo failed");
        return 1;
    }

    return 0;
}
"""

directory = "./tool/cfiles/99_sysinfo"
os.makedirs(directory, exist_ok=True)

filename = os.path.join(directory, "sysinfo_0.c")

with open(filename, "w") as f:
    f.write(template)
