import os

def generate_mlock_tests():
    output_dir = "./tool/cfiles/149_mlock"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/mman.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_mlock
#define SYS_mlock 149
#endif

int main() {
    long page_size = sysconf(_SC_PAGESIZE);
    if (page_size == -1) {
        return 1;
    }

    void *addr = mmap(NULL, page_size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) {
        return 1;
    }

    int result = syscall(SYS_mlock, addr, page_size);
    
    munmap(addr, page_size);

    if (result == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = f"{output_dir}/mlock_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_mlock_tests()
