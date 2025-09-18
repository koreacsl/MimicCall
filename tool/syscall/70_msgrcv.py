import os

def generate_msgrcv_tests():
    output_dir = "./tool/cfiles/70_msgrcv"
    os.makedirs(output_dir, exist_ok=True)

    msgrcv_flags = ["0", "IPC_NOWAIT", "MSG_EXCEPT", "MSG_NOERROR"]
    # -2 제거
    msg_types = ["1", "0"]

    for flag in msgrcv_flags:
        for mtype in msg_types:
            c_code = f"""#include <sys/ipc.h>
#include <sys/msg.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <string.h>

#ifndef SYS_msgget
#define SYS_msgget 68
#endif

#ifndef SYS_msgsnd
#define SYS_msgsnd 69
#endif

#ifndef SYS_msgrcv
#define SYS_msgrcv 70
#endif

#ifndef SYS_msgctl
#define SYS_msgctl 71
#endif

#ifndef MSG_EXCEPT
#define MSG_EXCEPT 2048
#endif

struct msgbuf {{
    long mtype;
    char mtext[32];
}};

int main() {{
    int msqid = syscall(SYS_msgget, IPC_PRIVATE, IPC_CREAT | S_IRUSR | S_IWUSR);
    if (msqid == -1) return 1;

    struct msgbuf message_to_send;
    message_to_send.mtype = 1;
    strcpy(message_to_send.mtext, "Test Message");
    if (syscall(SYS_msgsnd, msqid, &message_to_send, sizeof(message_to_send.mtext), 0) == -1) {{
        syscall(SYS_msgctl, msqid, IPC_RMID, NULL);
        return 1;
    }}

    struct msgbuf received_message;
    int result = syscall(SYS_msgrcv, msqid, &received_message, sizeof(received_message.mtext), {mtype}, {flag});

    syscall(SYS_msgctl, msqid, IPC_RMID, NULL);

    return (result == -1) ? 1 : 0;
}}
"""
            filename = os.path.join(output_dir, f"msgrcv_{flag.lower()}_type_{mtype}.c")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_msgrcv_tests()
