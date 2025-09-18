
import os

def generate_pkey_free_tests():
    output_dir = "./tool/cfiles/331_pkey_free"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>
#include <sys/mman.h>

#ifndef SYS_pkey_alloc
#define SYS_pkey_alloc 330
#endif
#ifndef SYS_pkey_free
#define SYS_pkey_free 331
#endif

int main() {
    int pkey = syscall(SYS_pkey_alloc, 0, 0);
    if (pkey == -1) {
        return 0;
    }

    if (syscall(SYS_pkey_free, pkey) == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "pkey_free_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_pkey_free_tests()
