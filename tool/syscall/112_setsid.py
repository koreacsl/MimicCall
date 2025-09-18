
import os

def generate_setsid_tests():
    output_dir = "./tool/cfiles/112_setsid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_setsid
#define SYS_setsid 112
#endif

int main() {
    syscall(SYS_setsid);
    return 0;
}
"""
    filename = os.path.join(output_dir, "setsid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_setsid_tests()
