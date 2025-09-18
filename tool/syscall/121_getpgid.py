
import os

def generate_getpgid_tests():
    output_dir = "./tool/cfiles/121_getpgid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_getpgid
#define SYS_getpgid 121
#endif

int main() {
    syscall(SYS_getpgid, 0);
    return 0;
}
"""
    filename = os.path.join(output_dir, "getpgid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_getpgid_tests()