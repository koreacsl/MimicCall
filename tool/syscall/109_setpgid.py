
import os

def generate_setpgid_tests():
    output_dir = "./tool/cfiles/109_setpgid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_setpgid
#define SYS_setpgid 109
#endif

int main() {
    syscall(SYS_setpgid, 0, 0);
    return 0;
}
"""
    filename = os.path.join(output_dir, "setpgid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_setpgid_tests()
