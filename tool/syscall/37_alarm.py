import os

template = """#define _GNU_SOURCE
#include <sys/syscall.h>
#include <stdio.h>
#include <unistd.h>

int main() {
    int remaining_time = syscall(SYS_alarm, 0);
    printf("Previous alarm remaining time: %d seconds\\n", remaining_time);

    if (remaining_time == 0) {
        printf("No previous alarm was set.\\n");
    }

    return 0;
}
"""

directory = "./tool/cfiles/37_alarm"
os.makedirs(directory, exist_ok=True)

filename = os.path.join(directory, "alarm_0.c")
with open(filename, "w") as f:
    f.write(template)

