import os

def generate_kill_tests():
    output_dir = "./tool/cfiles/62_kill"
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

#ifndef SYS_kill
#define SYS_kill 62
#endif

void handle_sigusr1(int sig) {{
}}

int main() {{
    pid_t child_pid = fork();

    if (child_pid == -1) {{
        return 1;
    }}

    if (child_pid == 0) {{
        if (strcmp("{signal_name}", "SIGUSR1") == 0) {{
            signal(SIGUSR1, handle_sigusr1);
        }}
        pause();
        _exit(0);
    }} else {{
        sleep(0.5);
        int result = syscall(SYS_kill, child_pid, {signal_name});
        
        if (result == -1 && strcmp("{signal_name}", "SIGKILL") != 0) {{
            kill(child_pid, SIGKILL);
        }}
        
        waitpid(child_pid, NULL, 0);
    }}

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"kill_{signal_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_kill_tests()

