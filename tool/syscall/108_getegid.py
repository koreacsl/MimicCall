
import os

def generate_getegid_tests():
    output_dir = "./tool/cfiles/108_getegid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_getegid
#define SYS_getegid 108
#endif

int main() {
    syscall(SYS_getegid);
    return 0;
}
"""
    filename = os.path.join(output_dir, "getegid_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_getegid_tests()
