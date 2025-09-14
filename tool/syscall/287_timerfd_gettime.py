# -*- coding: utf-8 -*-
import os

def generate_timerfd_gettime_tests():
    output_dir = "./tool/cfiles/287_timerfd_gettime"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/timerfd.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_timerfd_create
#define SYS_timerfd_create 283
#endif
#ifndef SYS_timerfd_settime
#define SYS_timerfd_settime 286
#endif
#ifndef SYS_timerfd_gettime
#define SYS_timerfd_gettime 287
#endif

int main() {
    int fd = syscall(SYS_timerfd_create, CLOCK_REALTIME, 0);
    if (fd == -1) return 1;

    struct itimerspec new_value;
    new_value.it_value.tv_sec = 1;
    new_value.it_value.tv_nsec = 0;
    new_value.it_interval.tv_sec = 0;
    new_value.it_interval.tv_nsec = 0;
    syscall(SYS_timerfd_settime, fd, 0, &new_value, NULL);

    struct itimerspec curr_value;
    if (syscall(SYS_timerfd_gettime, fd, &curr_value) == -1) {
        close(fd);
        return 1;
    }

    close(fd);
    return 0;
}
"""
    filename = os.path.join(output_dir, "timerfd_gettime_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_timerfd_gettime_tests()
