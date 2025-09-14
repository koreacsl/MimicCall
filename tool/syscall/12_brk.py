import itertools
import os

template = """#define _GNU_SOURCE
#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/syscall.h>

int main() {
    void *current_brk = sbrk(0);
    void *new_brk = (void *){intptr_value};
    
    if (syscall(SYS_brk, new_brk) == 0) {
        printf("brk succeeded: %p\\n", new_brk);
    } else {
        perror("brk failed");
    }
    return 0;
}
"""

directory = "./tool/cfiles/12_brk"
os.makedirs(directory, exist_ok=True)

intptr_values = ["sbrk(0)", "sbrk(0) + 0x1000"]

for i, intptr in enumerate(intptr_values):
    filename = os.path.join(directory, f"brk_{i}.c")
    with open(filename, "w") as f:
        f.write(template.replace("{intptr_value}", intptr))
