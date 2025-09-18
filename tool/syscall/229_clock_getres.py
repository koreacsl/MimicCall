
import os

def generate_clock_getres_tests():
    output_dir = "./tool/cfiles/229_clock_getres"
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

#ifndef SYS_clock_getres
#define SYS_clock_getres 229
#endif

int main() {{
    struct timespec res;

    if (syscall(SYS_clock_getres, {clock_id_str}, &res) == -1) {{
        return 1;
    }}

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"clock_getres_{clock_id_str.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_clock_getres_tests()
