
import os

def generate_swapoff_tests():
    output_dir = "./tool/cfiles/168_swapoff"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_swapoff
#define SYS_swapoff 168
#endif

int main() {
    const char *path = "/tmp/non_existent_swapfile";

    int result = syscall(SYS_swapoff, path);

    if (result == -1) {
        return 0;
    }

    return 1;
}
"""
    filename = os.path.join(output_dir, "swapoff_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_swapoff_tests()
