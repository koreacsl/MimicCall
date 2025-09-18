
import os

def generate_setgid_tests():
    output_dir = "./tool/cfiles/106_setgid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#ifndef SYS_setgid
#define SYS_setgid 106
#endif
#ifndef SYS_getgid
#define SYS_getgid 104
#endif

int main() {
    gid_t current_gid = syscall(SYS_getgid);
    syscall(SYS_setgid, current_gid);
    return 0;
}
"""
    filename = os.path.join(output_dir, "setgid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_setgid_tests()
