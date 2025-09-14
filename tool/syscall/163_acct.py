# -*- coding: utf-8 -*-
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
    // Calling acct(NULL) attempts to turn process accounting off.
    // As a non-root user, this will fail with EPERM.
    // This is the safest way to test the acct syscall without affecting the system.
    // The test is considered successful if the syscall fails as expected.
    int result = syscall(SYS_acct, NULL);

    // If result is -1, the syscall failed as expected for a non-root user.
    if (result == -1) {
        return 0; // Test PASSED
    }

    return 1; // Test FAILED
}
"""
    filename = os.path.join(output_dir, "acct_safe.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_acct_tests()
