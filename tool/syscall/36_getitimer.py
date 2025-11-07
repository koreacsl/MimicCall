import os

def generate_getitimer_tests():
    output_dir = "./tool/cfiles/36_getitimer"
    os.makedirs(output_dir, exist_ok=True)

    itimer_flags = ["ITIMER_REAL", "ITIMER_VIRTUAL", "ITIMER_PROF"]

    for flag in itimer_flags:
        c_code = f"""#define _GNU_SOURCE
#include <sys/time.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef SYS_setitimer
#define SYS_setitimer 38
#endif

#ifndef SYS_getitimer
#define SYS_getitimer 36
#endif

int main() {{
    struct itimerval set_value;
    set_value.it_value.tv_sec = 1;
    set_value.it_value.tv_usec = 0;
    set_value.it_interval.tv_sec = 0;
    set_value.it_interval.tv_usec = 0;

    if (syscall(SYS_setitimer, {flag}, &set_value, NULL) == -1) {{
        return 1;
    }}

    struct itimerval get_value;
    int result = syscall(SYS_getitimer, {flag}, &get_value);

    if (result == -1) {{
        return 1;
    }}

    return 0;
}}
"""
        filename = f"{output_dir}/getitimer_{flag.lower()}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_getitimer_tests()
