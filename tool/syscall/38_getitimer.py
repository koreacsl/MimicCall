import os

def generate_setitimer_tests():
    output_dir = "./tool/cfiles/38_setitimer"
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

int main() {{
    struct itimerval new_value;

    new_value.it_value.tv_sec = 1;
    new_value.it_value.tv_usec = 0;
    new_value.it_interval.tv_sec = 0;
    new_value.it_interval.tv_usec = 0;

    int result = syscall(SYS_setitimer, {flag}, &new_value, NULL);

    if (result == -1) {{
        return 1;
    }}

    return 0;
}}
"""
        filename = f"{output_dir}/setitimer_{flag.lower()}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_setitimer_tests()
