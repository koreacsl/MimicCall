# -*- coding: utf-8 -*-
import os

def generate_timer_getoverrun_tests():
    output_dir = "./tool/cfiles/225_timer_getoverrun"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <time.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <signal.h>

#ifndef SYS_timer_create
#define SYS_timer_create 222
#endif
#ifndef SYS_timer_getoverrun
#define SYS_timer_getoverrun 225
#endif
#ifndef SYS_timer_delete
#define SYS_timer_delete 226
#endif

int main() {
    timer_t timerid;
    struct sigevent sev = { .sigev_notify = SIGEV_NONE };

    if (syscall(SYS_timer_create, CLOCK_REALTIME, &sev, &timerid) == -1) return 1;

    if (syscall(SYS_timer_getoverrun, timerid) == -1) {
        syscall(SYS_timer_delete, timerid);
        return 1;
    }

    syscall(SYS_timer_delete, timerid);
    return 0;
}
"""
    filename = os.path.join(output_dir, "timer_getoverrun_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_timer_getoverrun_tests()
