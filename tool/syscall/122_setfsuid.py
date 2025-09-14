# -*- coding: utf-8 -*-
import os

def generate_setfsuid_tests():
    output_dir = "./tool/cfiles/122_setfsuid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#ifndef SYS_setfsuid
#define SYS_setfsuid 122
#endif
#ifndef SYS_getuid
#define SYS_getuid 102
#endif

int main() {
    uid_t current_uid = syscall(SYS_getuid);
    syscall(SYS_setfsuid, current_uid);
    return 0;
}
"""
    filename = os.path.join(output_dir, "setfsuid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_setfsuid_tests()