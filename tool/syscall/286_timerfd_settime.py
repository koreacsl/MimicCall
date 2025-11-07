
import os

def generate_timerfd_settime_tests():
    output_dir = "./tool/cfiles/286_timerfd_settime"
    os.makedirs(output_dir, exist_ok=True)

    settime_flags = {"relative": "0", "absolute": "TFD_TIMER_ABSTIME"}

    for flag_name, flag_value in settime_flags.items():
        c_code = f"""#include <sys/timerfd.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_timerfd_create
#define SYS_timerfd_create 283
#endif
#ifndef SYS_timerfd_settime
#define SYS_timerfd_settime 286
#endif

int main() {{
    int fd = syscall(SYS_timerfd_create, CLOCK_REALTIME, 0);
    if (fd == -1) return 1;

    struct itimerspec new_value;
    new_value.it_value.tv_sec = 1;
    new_value.it_value.tv_nsec = 0;
    new_value.it_interval.tv_sec = 0;
    new_value.it_interval.tv_nsec = 0;

    if (syscall(SYS_timerfd_settime, fd, {flag_value}, &new_value, NULL) == -1) {{
        close(fd);
        return 1;
    }}

    close(fd);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"timerfd_settime_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_timerfd_settime_tests()
