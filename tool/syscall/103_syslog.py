import os

template = '''#define _GNU_SOURCE
#include <sys/syslog.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <signal.h>

#ifndef SYSLOG_ACTION_CLOSE
#define SYSLOG_ACTION_CLOSE 0
#endif

#ifndef SYSLOG_ACTION_OPEN
#define SYSLOG_ACTION_OPEN 1
#endif

#ifndef SYSLOG_ACTION_READ
#define SYSLOG_ACTION_READ 2
#endif

#ifndef SYSLOG_ACTION_READ_ALL
#define SYSLOG_ACTION_READ_ALL 3
#endif

#ifndef SYSLOG_ACTION_READ_CLEAR
#define SYSLOG_ACTION_READ_CLEAR 4
#endif

#ifndef SYSLOG_ACTION_SIZE_UNREAD
#define SYSLOG_ACTION_SIZE_UNREAD 5
#endif

#ifndef SYSLOG_ACTION_SIZE_BUFFER
#define SYSLOG_ACTION_SIZE_BUFFER 6
#endif

void timeout_handler(int sig) {
    const char msg[] = "Execution timed out. Exiting...\\n";
    write(STDOUT_FILENO, msg, sizeof(msg) - 1);
    _exit(1);
}

int main(void) {
    int cmd = {syslog_cmd};
    char buffer[1024] = {0};
    int result;

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = timeout_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    if (sigaction(SIGALRM, &sa, NULL) < 0) {
        perror("sigaction failed");
        return 1;
    }
    alarm(3);

    struct rlimit rl = {.rlim_cur = 3, .rlim_max = 3};
    if (setrlimit(RLIMIT_CPU, &rl) < 0) {
        perror("setrlimit failed");
        return 1;
    }

    {setup_code}

    result = syscall(SYS_syslog, cmd, {buffer_arg}, {len_arg});
    if (result < 0) {
        perror("syslog failed");
        return 1;
    }

    {output_handling}

    return 0;
}
'''

directory = "./tool/cfiles/103_syslog"
os.makedirs(directory, exist_ok=True)

syslog_cmds = {
    "SYSLOG_ACTION_CLOSE":     {"buffer_arg": "NULL", "len_arg": "0", "output_handling": ""},
    "SYSLOG_ACTION_OPEN":      {"buffer_arg": "NULL", "len_arg": "0", "output_handling": ""},
    "SYSLOG_ACTION_SIZE_UNREAD": {"buffer_arg": "NULL", "len_arg": "0", "output_handling": 'printf("Unread syslog size: %d bytes\\n", result);'},
    "SYSLOG_ACTION_SIZE_BUFFER": {"buffer_arg": "NULL", "len_arg": "0", "output_handling": 'printf("Total syslog buffer size: %d bytes\\n", result);'}
}

for cmd, params in syslog_cmds.items():
    src = template.replace("{syslog_cmd}", cmd)
    src = src.replace("{buffer_arg}", params["buffer_arg"])
    src = src.replace("{len_arg}", params["len_arg"])
    src = src.replace("{setup_code}", "")
    src = src.replace("{output_handling}", params["output_handling"])

    filename = os.path.join(directory, f"syslog_{cmd}.c")
    with open(filename, "w") as f:
        f.write(src)