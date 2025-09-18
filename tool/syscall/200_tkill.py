import os

def generate_tkill_tests():
    output_dir = "./tool/cfiles/200_tkill"
    os.makedirs(output_dir, exist_ok=True)

    signals = ["SIGTERM", "SIGCONT", "SIGUSR1"]

    for signal_name in signals:

        c_code = f"""#define _GNU_SOURCE
#include <signal.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#ifndef SYS_tkill
#define SYS_tkill 200
#endif

#ifndef SYS_gettid
#define SYS_gettid 186
#endif

void handle_signal(int sig) {{
}}

int main() {{
    if (strcmp("{signal_name}", "SIGKILL") != 0 && strcmp("{signal_name}", "SIGSTOP") != 0) {{
        signal({signal_name}, handle_signal);
    }}
    
    pid_t tid = syscall(SYS_gettid);
    if (tid == -1) {{
        return 1;
    }}

    int result = syscall(SYS_tkill, tid, {signal_name});
    
    if (result == -1) {{
        return 1;
    }}

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"tkill_{signal_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_tkill_tests()

