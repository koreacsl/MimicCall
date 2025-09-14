import os

def generate_shmat_tests():
    output_dir = "./tool/cfiles/30_shmat"
    os.makedirs(output_dir, exist_ok=True)

    shmat_flags = [
        "0",
        "SHM_RDONLY",
        "SHM_RND",
        "SHM_REMAP"
    ]

    for flag in shmat_flags:
        flag_name = flag.lower().replace(" ", "")
        
        c_code = f"""#define _GNU_SOURCE
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef SYS_shmget
#define SYS_shmget 29
#endif

#ifndef SYS_shmat
#define SYS_shmat 30
#endif

#ifndef SYS_shmdt
#define SYS_shmdt 67
#endif

#ifndef SYS_shmctl
#define SYS_shmctl 31
#endif

int main() {{
    int shmid = shmget(IPC_PRIVATE, 4096, IPC_CREAT | S_IRUSR | S_IWUSR);
    if (shmid == -1) {{
        return 1;
    }}

    void *shmaddr = (void *)syscall(SYS_shmat, shmid, NULL, {flag});
    if (shmaddr == (void *)-1) {{
        shmctl(shmid, IPC_RMID, NULL);
        return 1;
    }}

    syscall(SYS_shmdt, shmaddr);
    syscall(SYS_shmctl, shmid, IPC_RMID, NULL);

    return 0;
}}
"""
        filename = f"{output_dir}/shmat_{flag_name}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_shmat_tests()
