# -*- coding: utf-8 -*-
import os

def generate_mlock2_tests():
    output_dir = "./tool/cfiles/325_mlock2"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/mman.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_mlock2
#define SYS_mlock2 325
#endif

int main() {
    void *addr = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) {
        return 1;
    }

    if (syscall(SYS_mlock2, addr, 4096, MLOCK_ONFAULT) == -1) {
        munmap(addr, 4096);
        return 1;
    }

    munmap(addr, 4096);
    return 0;
}
"""
    filename = f"{output_dir}/mlock2_onfault.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_mlock2_tests()
