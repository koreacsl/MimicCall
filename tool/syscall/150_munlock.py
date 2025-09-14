import os

def generate_munlock_tests():
    output_dir = "./tool/cfiles/150_munlock"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/mman.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_munlock
#define SYS_munlock 150
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

    mlock(addr, page_size);
    
    int result = syscall(SYS_munlock, addr, page_size);

    munmap(addr, page_size);

    if (result == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = f"{output_dir}/munlock_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_munlock_tests()
