import os

def generate_msgctl_tests():
    output_dir = "./tool/cfiles/71_msgctl"
    os.makedirs(output_dir, exist_ok=True)

    msgctl_commands = {
        "IPC_STAT": "IPC_STAT", 
        "IPC_SET": "IPC_SET",
        "IPC_INFO": "IPC_INFO",
        "MSG_INFO": "MSG_INFO",
        "MSG_STAT": "MSG_STAT"
    }

    for cmd_name, cmd_value in msgctl_commands.items():
        c_code = f"""#include <sys/ipc.h>
#include <sys/msg.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

#ifndef SYS_msgget
#define SYS_msgget 68
#endif

#ifndef SYS_msgctl
#define SYS_msgctl 71
#endif

#ifndef MSG_INFO
#define MSG_INFO 12
#endif
#ifndef MSG_STAT
#define MSG_STAT 11
#endif

int main() {{
    int msqid = syscall(SYS_msgget, IPC_PRIVATE, IPC_CREAT | S_IRUSR | S_IWUSR);
    if (msqid == -1) {{
        return 1;
    }}

    int result = 0;
    struct msqid_ds ds_buf;

    if (strcmp("{cmd_value}", "IPC_STAT") == 0) {{
        result = syscall(SYS_msgctl, msqid, {cmd_value}, &ds_buf);
    }} else if (strcmp("{cmd_value}", "IPC_SET") == 0) {{
        // First, get current stats to modify them
        if (syscall(SYS_msgctl, msqid, IPC_STAT, &ds_buf) == -1) {{
            syscall(SYS_msgctl, msqid, IPC_RMID, NULL);
            return 1;
        }}
        ds_buf.msg_qbytes = 16384;
        result = syscall(SYS_msgctl, msqid, {cmd_value}, &ds_buf);
    }} else if (strcmp("{cmd_value}", "IPC_INFO") == 0 || strcmp("{cmd_value}", "MSG_INFO") == 0) {{
        struct msginfo msg_info_buf;
        result = syscall(SYS_msgctl, 0, {cmd_value}, &msg_info_buf);
    }} else if (strcmp("{cmd_value}", "MSG_STAT") == 0) {{
        result = syscall(SYS_msgctl, 0, {cmd_value}, &ds_buf);
    }}

    syscall(SYS_msgctl, msqid, IPC_RMID, NULL);

    return (result == -1) ? 1 : 0;
}}
"""
        filename = os.path.join(output_dir, f"msgctl_{cmd_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_msgctl_tests()

