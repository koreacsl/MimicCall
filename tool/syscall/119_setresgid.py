
import os

def generate_setresgid_tests():
    output_dir = "./tool/cfiles/119_setresgid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#ifndef SYS_setresgid
#define SYS_setresgid 119
#endif
#ifndef SYS_getresgid
#define SYS_getresgid 120
#endif

int main() {
    gid_t rgid, egid, sgid;
    if (syscall(SYS_getresgid, &rgid, &egid, &sgid) == 0) {
        syscall(SYS_setresgid, rgid, egid, sgid);
    }
    return 0;
}
"""
    filename = os.path.join(output_dir, "setresgid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_setresgid_tests()