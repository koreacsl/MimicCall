# -*- coding: utf-8 -*-
import os

def generate_setreuid_tests():
    output_dir = "./tool/cfiles/113_setreuid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#ifndef SYS_setreuid
#define SYS_setreuid 113
#endif
#ifndef SYS_getuid
#define SYS_getuid 102
#endif
#ifndef SYS_geteuid
#define SYS_geteuid 107
#endif

int main() {
    uid_t ruid = syscall(SYS_getuid);
    uid_t euid = syscall(SYS_geteuid);
    syscall(SYS_setreuid, ruid, euid);
    return 0;
}
"""
    filename = os.path.join(output_dir, "setreuid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_setreuid_tests()
