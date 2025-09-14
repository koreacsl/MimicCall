import os

def generate_semop_tests():
    output_dir = "./tool/cfiles/65_semop"
    os.makedirs(output_dir, exist_ok=True)

    semop_flags = ["0", "IPC_NOWAIT"]

    for flag in semop_flags:
        c_code = f"""#include <sys/ipc.h>
#include <sys/sem.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef SYS_semget
#define SYS_semget 64
#endif

#ifndef SYS_semop
#define SYS_semop 65
#endif

#ifndef SYS_semctl
#define SYS_semctl 66
#endif

union semun {{
    int val;
    struct semid_ds *buf;
    unsigned short *array;
}};

int main() {{
    int semid = syscall(SYS_semget, IPC_PRIVATE, 1, IPC_CREAT | S_IRUSR | S_IWUSR);
    if (semid == -1) {{
        return 1;
    }}

    union semun arg;
    arg.val = 1;
    if (syscall(SYS_semctl, semid, 0, SETVAL, arg) == -1) {{
        syscall(SYS_semctl, semid, 0, IPC_RMID, 0);
        return 1;
    }}

    struct sembuf sops;
    sops.sem_num = 0;
    sops.sem_op = -1;
    sops.sem_flg = {flag};
    
    int result = syscall(SYS_semop, semid, &sops, 1);

    syscall(SYS_semctl, semid, 0, IPC_RMID, 0);
    
    return (result == -1) ? 1 : 0;
}}
"""
        filename = os.path.join(output_dir, f"semop_{flag}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_semop_tests()
