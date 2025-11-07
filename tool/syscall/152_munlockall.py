import os

def generate_munlockall_tests():
    output_dir = "./tool/cfiles/152_munlockall"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/mman.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_munlockall
#define SYS_munlockall 152
#endif

int main() {
    mlockall(MCL_CURRENT);
    
    int result = syscall(SYS_munlockall);

    if (result == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = f"{output_dir}/munlockall_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_munlockall_tests()
