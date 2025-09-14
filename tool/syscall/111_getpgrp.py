# -*- coding: utf-8 -*-
import os

def generate_getpgrp_tests():
    output_dir = "./tool/cfiles/111_getpgrp"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_getpgrp
#define SYS_getpgrp 111
#endif

int main() {
    syscall(SYS_getpgrp);
    return 0;
}
"""
    filename = os.path.join(output_dir, "getpgrp_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_getpgrp_tests()
