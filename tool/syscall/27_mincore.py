import os

def generate_mincore_test():
    output_dir = "./tool/cfiles/27_mincore"
    os.makedirs(output_dir, exist_ok=True)

    c_code = f"""#define _GNU_SOURCE
#include <unistd.h>
#include <sys/mman.h>
#include <stdio.h>
#include <errno.h>
#include <sys/syscall.h>

int main() {{
    size_t length = 4096;
    void *addr = mmap(NULL, length, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) return 1;

    unsigned char vec[1];

    int result = syscall(SYS_mincore, addr, length, vec);
    if (result == -1) return 1;

    munmap(addr, length);
    return 0;
}}
"""
    filename = f"{output_dir}/mincore_0.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_mincore_test()
