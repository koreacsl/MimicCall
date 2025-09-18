import os

template = """#define _GNU_SOURCE
#include <sys/syscall.h>
#include <stdio.h>
#include <unistd.h>

int main() {
    int remaining_time = syscall(SYS_alarm, 0);

    if (remaining_time == 0) {
    }

    return 0;
}
"""

directory = "./tool/cfiles/37_alarm"
os.makedirs(directory, exist_ok=True)

filename = os.path.join(directory, "alarm_0.c")
with open(filename, "w") as f:
    f.write(template)

