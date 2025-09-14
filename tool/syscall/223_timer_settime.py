# -*- coding: utf-8 -*-
import os

def generate_timer_settime_tests():
    output_dir = "./tool/cfiles/223_timer_settime"
    os.makedirs(output_dir, exist_ok=True)

    flags = {
        "relative": "0",
        "absolute": "TIMER_ABSTIME"
    }

    for flag_name, flag_value in flags.items():
        c_code = f"""#include <time.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <signal.h>

#ifndef SYS_timer_create
#define SYS_timer_create 222
#endif
#ifndef SYS_timer_settime
#define SYS_timer_settime 223
#endif
#ifndef SYS_timer_delete
#define SYS_timer_delete 226
#endif

int main() {{
    timer_t timerid;
    struct sigevent sev = {{ .sigev_notify = SIGEV_NONE }};
    struct itimerspec its;

    if (syscall(SYS_timer_create, CLOCK_REALTIME, &sev, &timerid) == -1) {{
        return 1;
    }}

    its.it_value.tv_sec = 1;
    its.it_value.tv_nsec = 0;
    its.it_interval.tv_sec = 0;
    its.it_interval.tv_nsec = 0;

    if (syscall(SYS_timer_settime, timerid, {flag_value}, &its, NULL) == -1) {{
        syscall(SYS_timer_delete, timerid);
        return 1;
    }}

    syscall(SYS_timer_delete, timerid);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"timer_settime_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_timer_settime_tests()
