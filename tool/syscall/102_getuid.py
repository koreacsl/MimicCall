
import os

def generate_getuid_tests():
    output_dir = "./tool/cfiles/102_getuid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_getuid
#define SYS_getuid 102
#endif

int main() {
    syscall(SYS_getuid);
    return 0;
}
"""
    filename = os.path.join(output_dir, "getuid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_getuid_tests()
