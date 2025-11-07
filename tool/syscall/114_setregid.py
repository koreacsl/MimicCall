
import os

def generate_setregid_tests():
    output_dir = "./tool/cfiles/114_setregid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#ifndef SYS_setregid
#define SYS_setregid 114
#endif
#ifndef SYS_getgid
#define SYS_getgid 104
#endif
#ifndef SYS_getegid
#define SYS_getegid 108
#endif

int main() {
    gid_t rgid = syscall(SYS_getgid);
    gid_t egid = syscall(SYS_getegid);
    syscall(SYS_setregid, rgid, egid);
    return 0;
}
"""
    filename = os.path.join(output_dir, "setregid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_setregid_tests()
