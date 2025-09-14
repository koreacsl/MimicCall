# -*- coding: utf-8 -*-
import os

def generate_getsid_tests():
    output_dir = "./tool/cfiles/124_getsid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_getsid
#define SYS_getsid 124
#endif

int main() {
    syscall(SYS_getsid, 0);
    return 0;
}
"""
    filename = os.path.join(output_dir, "getsid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_getsid_tests()