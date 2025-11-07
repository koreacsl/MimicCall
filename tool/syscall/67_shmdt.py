import os

def generate_shmdt_test():
    output_dir = "./tool/cfiles/67_shmdt"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
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

int main() {
    int shmid = shmget(IPC_PRIVATE, 4096, IPC_CREAT | S_IRUSR | S_IWUSR);
    if (shmid == -1) {
        return 1;
    }

    void *shmaddr = (void *)shmat(shmid, NULL, 0);
    if (shmaddr == (void *)-1) {
        shmctl(shmid, IPC_RMID, NULL);
        return 1;
    }

    int result = syscall(SYS_shmdt, shmaddr);

    shmctl(shmid, IPC_RMID, NULL);

    if (result == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = f"{output_dir}/shmdt_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_shmdt_test()
