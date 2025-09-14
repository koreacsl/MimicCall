import os

template = '''#define _GNU_SOURCE
#include <sys/syscall.h>
#include <asm/unistd.h>
#include <sys/stat.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <stdlib.h>

#ifndef SYS_umask
#define SYS_umask 95
#endif

int main(void) {
    mode_t new_mask = {umask_value};
    mode_t old_mask;
    
    old_mask = syscall(SYS_umask, new_mask);
    if (old_mask == (mode_t)-1) {
        perror("umask syscall failed");
        return 1;
    }

    if (syscall(SYS_umask, old_mask) == (mode_t)-1) {
        perror("restore umask failed");
        return 1;
    }

    return 0;
}
'''

directory = "./tool/cfiles/95_umask"
os.makedirs(directory, exist_ok=True)

umask_values = ["000", "022", "077", "002"]

for idx, val in enumerate(umask_values):
    src = template.replace("{umask_value}", val)
    filename = os.path.join(directory, f"umask_{idx}_{val}.c")
    with open(filename, "w") as f:
        f.write(src)