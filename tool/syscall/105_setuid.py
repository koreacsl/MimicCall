
import os

def generate_setuid_tests():
    output_dir = "./tool/cfiles/105_setuid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#ifndef SYS_setuid
#define SYS_setuid 105
#endif
#ifndef SYS_getuid
#define SYS_getuid 102
#endif

int main() {
    uid_t current_uid = syscall(SYS_getuid);
    syscall(SYS_setuid, current_uid);
    return 0;
}
"""
    filename = os.path.join(output_dir, "setuid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_setuid_tests()
