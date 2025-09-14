import os

def generate_tgkill_tests():
    output_dir = "./tool/cfiles/234_tgkill"
    os.makedirs(output_dir, exist_ok=True)

    signals = ["SIGTERM", "SIGKILL", "SIGSTOP", "SIGCONT", "SIGUSR1"]

    for signal_name in signals:

        c_code = f"""#define _GNU_SOURCE
#include <signal.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#ifndef SYS_tgkill
#define SYS_tgkill 234
#endif

void handle_signal(int sig) {{
    _exit(0);
}}

int main() {{
    pid_t child_pid = fork();

    if (child_pid == -1) {{
        return 1;
    }}

    if (child_pid == 0) {{
        if (strcmp("{signal_name}", "SIGKILL") != 0 && strcmp("{signal_name}", "SIGSTOP") != 0) {{
            signal({signal_name}, handle_signal);
        }}
        pause();
        _exit(1);
    }} else {{
        sleep(1);
        
        int result = syscall(SYS_tgkill, child_pid, child_pid, {signal_name});

        if (result == -1 && strcmp("{signal_name}", "SIGKILL") != 0) {{
            kill(child_pid, SIGKILL);
        }}
        
        waitpid(child_pid, NULL, 0);
    }}

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"tgkill_{signal_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_tgkill_tests()

