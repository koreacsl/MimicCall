# -*- coding: utf-8 -*-
import os

def generate_getgroups_tests():
    output_dir = "./tool/cfiles/115_getgroups"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#ifndef SYS_getgroups
#define SYS_getgroups 115
#endif

int main() {
    gid_t list[32];
    syscall(SYS_getgroups, 32, list);
    return 0;
}
"""
    filename = os.path.join(output_dir, "getgroups_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_getgroups_tests()
