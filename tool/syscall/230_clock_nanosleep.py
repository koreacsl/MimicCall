import os

template = """#define _GNU_SOURCE
#include <time.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <stdlib.h>

int main() {
    struct timespec tp;
    syscall(SYS_clock_gettime, {clock_id}, &tp);
    tp.tv_nsec += 100000000;

    int result = syscall(SYS_clock_nanosleep, {clock_id}, TIMER_ABSTIME, &tp, NULL);

    if (result == -1) {
        perror("clock_nanosleep failed");
        exit(1);
    }

    exit(0);
}
"""

directory = "./tool/cfiles/230_clock_nanosleep"
os.makedirs(directory, exist_ok=True)

clock_ids = ["CLOCK_REALTIME", "CLOCK_MONOTONIC", "CLOCK_BOOTTIME"]

for clock_id in clock_ids:
    filename = os.path.join(directory, f"clock_nanosleep_{clock_id}_TIMER_ABSTIME.c")
    with open(filename, "w") as f:
        f.write(template.replace("{clock_id}", clock_id))
