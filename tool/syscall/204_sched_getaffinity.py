# -*- coding: utf-8 -*-
import os

def generate_sched_getaffinity_tests():
    output_dir = "./tool/cfiles/204_sched_getaffinity"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
#include <sched.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_sched_getaffinity
#define SYS_sched_getaffinity 204
#endif

int main() {
    pid_t pid = getpid();
    cpu_set_t mask;

    CPU_ZERO(&mask);

    // sched_getaffinity is a read-only operation and is inherently safe.
    if (syscall(SYS_sched_getaffinity, pid, sizeof(mask), &mask) == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "sched_getaffinity_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_sched_getaffinity_tests()
