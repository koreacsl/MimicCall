# -*- coding: utf-8 -*-
import os

def generate_setgroups_tests():
    output_dir = "./tool/cfiles/116_setgroups"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#ifndef SYS_setgroups
#define SYS_setgroups 116
#endif
#ifndef SYS_getgroups
#define SYS_getgroups 115
#endif

int main() {
    gid_t list[32];
    int n = syscall(SYS_getgroups, 32, list);
    if (n >= 0) {
        syscall(SYS_setgroups, n, list);
    }
    return 0;
}
"""
    filename = os.path.join(output_dir, "setgroups_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_setgroups_tests()
