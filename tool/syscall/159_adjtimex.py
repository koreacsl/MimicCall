# -*- coding: utf-8 -*-
import os

def generate_adjtimex_tests():
    output_dir = "./tool/cfiles/159_adjtimex"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/timex.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <string.h>

#ifndef SYS_adjtimex
#define SYS_adjtimex 159
#endif

int main() {
    struct timex tx;

    memset(&tx, 0, sizeof(tx));

    if (syscall(SYS_adjtimex, &tx) < 0) {
        return 1;
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "adjtimex_readonly.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_adjtimex_tests()
