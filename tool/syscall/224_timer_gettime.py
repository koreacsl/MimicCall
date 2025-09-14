# -*- coding: utf-8 -*-
import os

def generate_timer_gettime_tests():
    output_dir = "./tool/cfiles/224_timer_gettime"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <time.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <signal.h>

#ifndef SYS_timer_create
#define SYS_timer_create 222
#endif
#ifndef SYS_timer_settime
#define SYS_timer_settime 223
#endif
#ifndef SYS_timer_gettime
#define SYS_timer_gettime 224
#endif
#ifndef SYS_timer_delete
#define SYS_timer_delete 226
#endif

int main() {
    timer_t timerid;
    struct sigevent sev = { .sigev_notify = SIGEV_NONE };
    struct itimerspec its, current_its;

    if (syscall(SYS_timer_create, CLOCK_REALTIME, &sev, &timerid) == -1) return 1;

    its.it_value.tv_sec = 1;
    its.it_value.tv_nsec = 0;
    its.it_interval.tv_sec = 0;
    its.it_interval.tv_nsec = 0;
    syscall(SYS_timer_settime, timerid, 0, &its, NULL);

    if (syscall(SYS_timer_gettime, timerid, &current_its) == -1) {
        syscall(SYS_timer_delete, timerid);
        return 1;
    }

    syscall(SYS_timer_delete, timerid);
    return 0;
}
"""
    filename = os.path.join(output_dir, "timer_gettime.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_timer_gettime_tests()
