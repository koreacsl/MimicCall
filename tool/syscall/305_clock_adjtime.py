# -*- coding: utf-8 -*-
import os

def generate_clock_adjtime_tests():
    output_dir = "./tool/cfiles/305_clock_adjtime"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <time.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/timex.h>

#ifndef SYS_clock_adjtime
#define SYS_clock_adjtime 305
#endif

int main() {
    if (syscall(SYS_clock_adjtime, CLOCK_REALTIME, NULL) < 0) {
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "clock_adjtime.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_clock_adjtime_tests()
