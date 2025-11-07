
import os

def generate_geteuid_tests():
    output_dir = "./tool/cfiles/107_geteuid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_geteuid
#define SYS_geteuid 107
#endif

int main() {
    syscall(SYS_geteuid);
    return 0;
}
"""
    filename = os.path.join(output_dir, "geteuid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_geteuid_tests()
