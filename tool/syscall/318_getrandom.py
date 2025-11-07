import os

template = """#define _GNU_SOURCE
#include <sys/random.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

#ifndef GRND_NONBLOCK
#define GRND_NONBLOCK 0x0001
#endif

#ifndef GRND_RANDOM
#define GRND_RANDOM 0x0002
#endif

int main() {
    unsigned char buffer[16];
    int len = sizeof(buffer);
    int flags = {getrandom_flag};

    ssize_t result = syscall(SYS_getrandom, buffer, len, flags);
    if (result == -1) {
        perror("getrandom failed");
        return 1;
    }

    return 0;
}
"""

directory = "./tool/cfiles/318_getrandom"
os.makedirs(directory, exist_ok=True)

getrandom_flags = [
    "0",               
    "GRND_NONBLOCK",   
    "GRND_RANDOM"      
]

for flag in getrandom_flags:
    filename = os.path.join(directory, f"getrandom_{flag}.c")
    with open(filename, "w") as f:
        f.write(template.replace("{getrandom_flag}", flag))
