
import os

def generate_clock_gettime_tests():
    output_dir = "./tool/cfiles/228_clock_gettime"
    os.makedirs(output_dir, exist_ok=True)

    clock_ids = [
        "CLOCK_REALTIME", "CLOCK_MONOTONIC", 
        "CLOCK_PROCESS_CPUTIME_ID", "CLOCK_THREAD_CPUTIME_ID",
        "CLOCK_BOOTTIME"
    ]

    for clock_id_str in clock_ids:
        c_code = f"""#include <time.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_clock_gettime
#define SYS_clock_gettime 228
#endif

int main() {{
    struct timespec tp;

    if (syscall(SYS_clock_gettime, {clock_id_str}, &tp) == -1) {{
        return 1;
    }}

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"clock_gettime_{clock_id_str.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_clock_gettime_tests()
