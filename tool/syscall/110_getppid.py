
import os

def generate_getppid_tests():
    output_dir = "./tool/cfiles/110_getppid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_getppid
#define SYS_getppid 110
#endif

int main() {
    syscall(SYS_getppid);
    return 0;
}
"""
    filename = os.path.join(output_dir, "getppid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_getppid_tests()
