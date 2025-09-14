# -*- coding: utf-8 -*-
import os

def generate_exit_group_tests():
    output_dir = "./tool/cfiles/231_exit_group"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_exit_group
#define SYS_exit_group 231
#endif

int main() {
    syscall(SYS_exit_group, 0);

    return 1;
}
"""
    filename = os.path.join(output_dir, "exit_group_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_exit_group_tests()
