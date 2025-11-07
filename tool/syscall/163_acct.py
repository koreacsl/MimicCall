
import os

def generate_acct_tests():
    output_dir = "./tool/cfiles/163_acct"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_acct
#define SYS_acct 163
#endif

int main() {
    int result = syscall(SYS_acct, NULL);

    if (result == -1) {
        return 0;
    }

    return 1;
}
"""
    filename = os.path.join(output_dir, "acct_safe.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_acct_tests()
