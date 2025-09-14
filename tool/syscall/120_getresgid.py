# -*- coding: utf-8 -*-
import os

def generate_getresgid_tests():
    output_dir = "./tool/cfiles/120_getresgid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#ifndef SYS_getresgid
#define SYS_getresgid 120
#endif

int main() {
    gid_t rgid, egid, sgid;
    syscall(SYS_getresgid, &rgid, &egid, &sgid);
    return 0;
}
"""
    filename = os.path.join(output_dir, "getresgid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_getresgid_tests()