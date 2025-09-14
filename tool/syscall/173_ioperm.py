import os

template = """#define _GNU_SOURCE
#include <sys/io.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>

int main() {
    unsigned long from = {ioperm_from};
    unsigned long num = {ioperm_num};
    int turn_on = {ioperm_on};

    int result = syscall(SYS_ioperm, from, num, turn_on);
    if (result == -1) {
        perror("ioperm failed");
        return 1;
    }

    if (turn_on) {
        syscall(SYS_ioperm, from, num, 0);
    }

    return 0;
}
"""

directory = "./tool/cfiles/173_ioperm"
os.makedirs(directory, exist_ok=True)

ioperm_tests = [
    {"from": "0x3f8", "num": "8", "on": "1"},
    {"from": "0x378", "num": "8", "on": "1"},
    {"from": "0x3f8", "num": "8", "on": "0"},
]

for i, test in enumerate(ioperm_tests):
    filename = os.path.join(directory, f"ioperm_{i}.c")
    with open(filename, "w") as f:
        f.write(template.replace("{ioperm_from}", test["from"])
                        .replace("{ioperm_num}", test["num"])
                        .replace("{ioperm_on}", test["on"]))
