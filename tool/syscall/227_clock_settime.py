# -*- coding: utf-8 -*-
import os

def generate_clock_settime_tests():
    output_dir = "./tool/cfiles/227_clock_settime"
    os.makedirs(output_dir, exist_ok=True)

    clock_id_str = "CLOCK_REALTIME"

    c_code = f"""#include <time.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_clock_gettime
#define SYS_clock_gettime 228
#endif
#ifndef SYS_clock_settime
#define SYS_clock_settime 227
#endif

int main() {{
    struct timespec tp;

    if (syscall(SYS_clock_gettime, {clock_id_str}, &tp) == -1) {{
        return 1;
    }}

    syscall(SYS_clock_settime, {clock_id_str}, &tp);

    return 0;
}}
"""
    filename = os.path.join(output_dir, f"clock_settime_{clock_id_str.lower()}_safe.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_clock_settime_tests()