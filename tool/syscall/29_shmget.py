import os

def generate_shmget_tests():
    output_dir = "./tool/cfiles/29_shmget"
    os.makedirs(output_dir, exist_ok=True)

    shmget_flags = [
        "IPC_CREAT",
        "IPC_CREAT | IPC_EXCL",
        "SHM_HUGETLB",
        "SHM_NORESERVE"
    ]
    permission_flags = ["S_IRUSR | S_IWUSR", "S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH"]

    for flag in shmget_flags:
        for perm in permission_flags:
            flag_str = f"{flag} | {perm}"
            flag_name = flag.lower().replace(" ", "").replace("|", "") + "_" + perm.lower().replace(" ", "").replace("|", "_")
            
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
    int shmid = syscall(SYS_shmget, IPC_PRIVATE, 4096, {flag_str});
    if (shmid == -1) {{
        return 1;
    }}

    syscall(SYS_shmctl, shmid, IPC_RMID, NULL);

    return 0;
}}
"""
            filename = f"{output_dir}/shmget_{flag_name}.c"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_shmget_tests()
