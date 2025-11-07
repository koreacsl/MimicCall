
import os

def generate_setresuid_tests():
    output_dir = "./tool/cfiles/117_setresuid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#ifndef SYS_setresuid
#define SYS_setresuid 117
#endif
#ifndef SYS_getresuid
#define SYS_getresuid 118
#endif

int main() {
    uid_t ruid, euid, suid;
    if (syscall(SYS_getresuid, &ruid, &euid, &suid) == 0) {
        syscall(SYS_setresuid, ruid, euid, suid);
    }
    return 0;
}
"""
    filename = os.path.join(output_dir, "setresuid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_setresuid_tests()

