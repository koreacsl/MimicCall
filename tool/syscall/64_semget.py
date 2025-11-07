import os

def generate_semget_tests():
    output_dir = "./tool/cfiles/64_semget"
    os.makedirs(output_dir, exist_ok=True)

    semget_flags = [
        "IPC_CREAT | S_IRUSR | S_IWUSR",
        "IPC_CREAT | IPC_EXCL | S_IRUSR | S_IWUSR",
        "IPC_CREAT | S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP",
        "IPC_CREAT | S_IRUSR | S_IWUSR | S_IROTH | S_IWOTH"
    ]

    for flag in semget_flags:
        flag_name = flag.lower().replace(" | ", "_")
        c_code = f"""#include <sys/ipc.h>
#include <sys/sem.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef SYS_semget
#define SYS_semget 64
#endif

#ifndef SYS_semctl
#define SYS_semctl 66
#endif

int main() {{
    int semid = syscall(SYS_semget, IPC_PRIVATE, 1, {flag});
    if (semid == -1) {{
        return 1;
    }}

    syscall(SYS_semctl, semid, 0, IPC_RMID, 0);

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"semget_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_semget_tests()
