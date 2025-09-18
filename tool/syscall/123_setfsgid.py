
import os

def generate_setfsgid_tests():
    output_dir = "./tool/cfiles/123_setfsgid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#ifndef SYS_setfsgid
#define SYS_setfsgid 123
#endif
#ifndef SYS_getgid
#define SYS_getgid 104
#endif

int main() {
    gid_t current_gid = syscall(SYS_getgid);
    syscall(SYS_setfsgid, current_gid);
    return 0;
}
"""
    filename = os.path.join(output_dir, "setfsgid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_setfsgid_tests()