import os

def generate_shmctl_tests():
    output_dir = "./tool/cfiles/31_shmctl"
    os.makedirs(output_dir, exist_ok=True)

    shmctl_commands = [
        "IPC_STAT",
        "IPC_SET",
        "SHM_LOCK",
        "SHM_UNLOCK"
    ]

    for cmd in shmctl_commands:
        cmd_name = cmd.lower()
        
        c_code = f"""#define _GNU_SOURCE
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef SYS_shmget
#define SYS_shmget 29
#endif

#ifndef SYS_shmctl
#define SYS_shmctl 31
#endif

int main() {{
    int shmid = shmget(IPC_PRIVATE, 4096, IPC_CREAT | S_IRUSR | S_IWUSR);
    if (shmid == -1) {{
        return 1;
    }}

    struct shmid_ds ds_buf;
    int result = 0;

    if ({cmd} == IPC_SET) {{
        if(syscall(SYS_shmctl, shmid, IPC_STAT, &ds_buf) == -1) {{
            syscall(SYS_shmctl, shmid, IPC_RMID, NULL);
            return 1;
        }}
        result = syscall(SYS_shmctl, shmid, IPC_SET, &ds_buf);
    }} else {{
        result = syscall(SYS_shmctl, shmid, {cmd}, &ds_buf);
    }}

    syscall(SYS_shmctl, shmid, IPC_RMID, NULL);

    if (result == -1) {{
        return 1;
    }}

    return 0;
}}
"""
        filename = f"{output_dir}/shmctl_{cmd_name}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_shmctl_tests()
