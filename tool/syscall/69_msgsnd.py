import os

def generate_msgsnd_tests():
    output_dir = "./tool/cfiles/69_msgsnd"
    os.makedirs(output_dir, exist_ok=True)

    msgsnd_flags = ["0", "IPC_NOWAIT"]

    for flag in msgsnd_flags:
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

#ifndef SYS_msgctl
#define SYS_msgctl 71
#endif

struct msgbuf {{
    long mtype;
    char mtext[32];
}};

int main() {{
    int msqid = syscall(SYS_msgget, IPC_PRIVATE, IPC_CREAT | S_IRUSR | S_IWUSR);
    if (msqid == -1) {{
        return 1;
    }}

    struct msgbuf message;
    message.mtype = 1;
    strcpy(message.mtext, "test");

    int result = syscall(SYS_msgsnd, msqid, &message, sizeof(message.mtext), {flag});

    syscall(SYS_msgctl, msqid, IPC_RMID, NULL);

    return (result == -1) ? 1 : 0;
}}
"""
        filename = os.path.join(output_dir, f"msgsnd_{flag}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_msgsnd_tests()
