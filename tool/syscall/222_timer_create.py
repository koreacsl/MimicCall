
import os

def generate_timer_create_tests():
    output_dir = "./tool/cfiles/222_timer_create"
    os.makedirs(output_dir, exist_ok=True)

    clock_ids = [
        "CLOCK_REALTIME", "CLOCK_MONOTONIC", "CLOCK_PROCESS_CPUTIME_ID", "CLOCK_THREAD_CPUTIME_ID"
    ]

    for clock_id_str in clock_ids:
        c_code = f"""#include <time.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <signal.h>

#ifndef SYS_timer_create
#define SYS_timer_create 222
#endif
#ifndef SYS_timer_delete
#define SYS_timer_delete 226
#endif

int main() {{
    timer_t timerid;
    struct sigevent sev;

    sev.sigev_notify = SIGEV_NONE;
    sev.sigev_signo = 0;
    sev.sigev_value.sival_ptr = NULL;

    if (syscall(SYS_timer_create, {clock_id_str}, &sev, &timerid) == -1) {{
        return 1;
    }}

    syscall(SYS_timer_delete, timerid);

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"timer_create_{clock_id_str.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_timer_create_tests()
