
import os

def generate_timerfd_create_tests():
    output_dir = "./tool/cfiles/283_timerfd_create"
    os.makedirs(output_dir, exist_ok=True)

    clock_ids = ["CLOCK_REALTIME", "CLOCK_MONOTONIC"]
    create_flags = {"none": "0", "nonblock": "TFD_NONBLOCK", "cloexec": "TFD_CLOEXEC"}

    for clock_str in clock_ids:
        for flag_name, flag_value in create_flags.items():
            c_code = f"""#include <sys/timerfd.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_timerfd_create
#define SYS_timerfd_create 283
#endif

int main() {{
    int fd = syscall(SYS_timerfd_create, {clock_str}, {flag_value});
    if (fd == -1) {{
        return 1;
    }}
    close(fd);
    return 0;
}}
"""
            filename = os.path.join(output_dir, f"timerfd_create_{clock_str.lower()}_{flag_name}.c")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_timerfd_create_tests()
