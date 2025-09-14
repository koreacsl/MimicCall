# -*- coding: utf-8 -*-
import os

def generate_times_tests():
    output_dir = "./tool/cfiles/100_times"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/times.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_times
#define SYS_times 100
#endif

int main() {
    struct tms buf;

    if (syscall(SYS_times, &buf) == (clock_t)-1) {
        return 1;
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "times_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_times_tests()
