import os

template = """#define _GNU_SOURCE
#include <time.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <stdlib.h>

int main() {
    struct timespec req, rem;

    req.tv_sec = {seconds};
    req.tv_nsec = {nanoseconds};

    int result = syscall(SYS_nanosleep, &req, &rem);

    if (result == -1) {
        perror("nanosleep failed");
        exit(1);
    }

    printf("Sleep completed successfully.\\n");
    exit(0);
}
"""

source_directory = "./tool/cfiles/35_nanosleep"

os.makedirs(source_directory, exist_ok=True)

sleep_times = [
    (0, 500000000),
    (1, 0),
    (2, 500000000),
    (0, 100000000),
]

for seconds, nanoseconds in sleep_times:
    source_filename = os.path.join(source_directory, f"nanosleep_{seconds}_{nanoseconds}.c")

    with open(source_filename, "w") as f:
        f.write(template.replace("{seconds}", str(seconds)).replace("{nanoseconds}", str(nanoseconds)))
