
import os

def generate_chroot_tests():
    output_dir = "./tool/cfiles/161_chroot"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_chroot
#define SYS_chroot 161
#endif

int main() {
    int result = syscall(SYS_chroot, "/");

    if (result == -1) {
        return 0;
    }

    return 1;
}
"""
    filename = os.path.join(output_dir, "chroot_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_chroot_tests()
