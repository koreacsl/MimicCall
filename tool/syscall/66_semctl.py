import os

def generate_semctl_tests():
    output_dir = "./tool/cfiles/66_semctl"
    os.makedirs(output_dir, exist_ok=True)

    semctl_commands = {
        "IPC_STAT": "IPC_STAT", "IPC_SET": "IPC_SET", "GETALL": "GETALL",
        "GETNCNT": "GETNCNT", "GETPID": "GETPID", "GETVAL": "GETVAL",
        "GETZCNT": "GETZCNT", "SETALL": "SETALL", "SETVAL": "SETVAL"
    }

    for cmd_name, cmd_value in semctl_commands.items():
        c_code = f"""#include <sys/ipc.h>
#include <sys/sem.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#ifndef SYS_semget
#define SYS_semget 64
#endif

#ifndef SYS_semctl
#define SYS_semctl 66
#endif

union semun {{
    int val;
    struct semid_ds *buf;
    unsigned short *array;
    struct seminfo *__buf;
}};

int main() {{
    int semid = syscall(SYS_semget, IPC_PRIVATE, 1, IPC_CREAT | S_IRUSR | S_IWUSR);
    if (semid == -1) {{
        return 1;
    }}

    int result = 0;
    union semun arg;

    if (strcmp("{cmd_value}", "IPC_STAT") == 0) {{
        struct semid_ds ds_buf;
        arg.buf = &ds_buf;
        result = syscall(SYS_semctl, semid, 0, {cmd_value}, arg);
    }} else if (strcmp("{cmd_value}", "IPC_SET") == 0) {{
        struct semid_ds ds_buf;
        syscall(SYS_semctl, semid, 0, IPC_STAT, &ds_buf);
        ds_buf.sem_perm.uid = getuid();
        ds_buf.sem_perm.gid = getgid();
        arg.buf = &ds_buf;
        result = syscall(SYS_semctl, semid, 0, {cmd_value}, arg);
    }} else if (strcmp("{cmd_value}", "GETALL") == 0) {{
        unsigned short arr[1];
        arg.array = arr;
        result = syscall(SYS_semctl, semid, 0, {cmd_value}, arg);
    }} else if (strcmp("{cmd_value}", "SETALL") == 0) {{
        unsigned short arr[1] = {{1}};
        arg.array = arr;
        result = syscall(SYS_semctl, semid, 0, {cmd_value}, arg);
    }} else if (strcmp("{cmd_value}", "SETVAL") == 0) {{
        arg.val = 1;
        result = syscall(SYS_semctl, semid, 0, {cmd_value}, arg);
    }} else {{
        result = syscall(SYS_semctl, semid, 0, {cmd_value}, 0);
    }}

    syscall(SYS_semctl, semid, 0, IPC_RMID, 0);

    return (result == -1) ? 1 : 0;
}}
"""
        filename = os.path.join(output_dir, f"semctl_{cmd_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_semctl_tests()
