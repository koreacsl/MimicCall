
import os

output_dir = "./tool/cfiles/220_semtimedop"
os.makedirs(output_dir, exist_ok=True)

header = '''#define _GNU_SOURCE
#include <unistd.h>
#include <stdint.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/sem.h>
#include <sys/syscall.h>
#include <fcntl.h>
#include <time.h>

#ifndef SYS_semget
#define SYS_semget 64
#endif

#ifndef SYS_semtimedop
#define SYS_semtimedop 221
#endif
'''

semget_flags = [
    "IPC_CREAT", "IPC_EXCL", "S_IRUSR", "S_IWUSR", "S_IXUSR",
    "S_IRGRP", "S_IWGRP", "S_IXGRP", "S_IROTH", "S_IWOTH", "S_IXOTH"
]

semop_flags = ["0", "IPC_NOWAIT", "SEM_UNDO"]

def write_test(filename, content):
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)

for flag in semget_flags:
    code = f"""{header}
int main() {{
    syscall(SYS_semget, IPC_PRIVATE, 1, {flag});
    return 0;
}}
"""
    write_test(f"semget_{flag.lower()}.c", code)

for flag in semop_flags:
    code = f"""{header}
int main() {{
    struct sembuf sops[1] = {{ {{0, 0, {flag}}} }};
    struct timespec timeout = {{1, 0}};
    syscall(SYS_semtimedop, 0, sops, 1, &timeout);
    return 0;
}}
"""
    write_test(f"semtimedop_{flag.lower()}.c", code)
