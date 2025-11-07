import os

template = """#define _GNU_SOURCE
#include <sys/utsname.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>

int main() {
    struct utsname buf;

    if (syscall(SYS_uname, &buf) == -1) {
        perror("syscall(SYS_uname) failed");
        return 1;
    }

    return 0;
}
"""

directory = "./tool/cfiles/63_uname"
os.makedirs(directory, exist_ok=True)

filename = os.path.join(directory, "uname_0.c")

with open(filename, "w") as f:
    f.write(template)
