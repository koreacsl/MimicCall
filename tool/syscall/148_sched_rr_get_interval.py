import os

template = """#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <errno.h>
#include <time.h>

int main() {
    pid_t pid = getpid();
    struct timespec tp;

    if (syscall(SYS_sched_rr_get_interval, pid, &tp) == -1) {
        perror("sched_rr_get_interval failed");
        return 1;
    }

    return 0;
}
"""

directory = "./tool/cfiles/148_sched_rr_get_interval"
os.makedirs(directory, exist_ok=True)

filename = os.path.join(directory, f"sched_rr_get_interval_0.c")
with open(filename, "w") as f:
    f.write(template)
