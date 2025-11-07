import os

def generate_msgget_tests():
    output_dir = "./tool/cfiles/68_msgget"
    os.makedirs(output_dir, exist_ok=True)

    msgget_flags = [
        "IPC_CREAT | S_IRUSR | S_IWUSR",
        "IPC_CREAT | IPC_EXCL | S_IRUSR | S_IWUSR",
        "IPC_CREAT | S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP",
        "IPC_CREAT | S_IRUSR | S_IWUSR | S_IROTH | S_IWOTH"
    ]

    for flag in msgget_flags:
        flag_name = flag.lower().replace(" | ", "_")
        c_code = f"""#include <sys/ipc.h>
#include <sys/msg.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef SYS_msgget
#define SYS_msgget 68
#endif

#ifndef SYS_msgctl
#define SYS_msgctl 71
#endif

int main() {{
    int msqid = syscall(SYS_msgget, IPC_PRIVATE, {flag});
    if (msqid == -1) {{
        return 1;
    }}

    syscall(SYS_msgctl, msqid, IPC_RMID, NULL);

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"msgget_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_msgget_tests()
