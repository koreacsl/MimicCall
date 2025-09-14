# -*- coding: utf-8 -*-
import os

def generate_sched_getparam_tests():
    output_dir = "./tool/cfiles/143_sched_getparam"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sched.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_sched_getparam
#define SYS_sched_getparam 143
#endif

int main() {
    pid_t pid = getpid();
    struct sched_param param;

    if (syscall(SYS_sched_getparam, pid, &param) == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "sched_getparam.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_sched_getparam_tests()
