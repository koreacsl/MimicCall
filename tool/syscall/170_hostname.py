# -*- coding: utf-8 -*-
import os

def generate_sethostname_tests():
    output_dir = "./tool/cfiles/170_sethostname"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
#include <unistd.h>
#include <string.h>
#include <sys/syscall.h>

#ifndef SYS_sethostname
#define SYS_sethostname 170
#endif

#define HOST_NAME_MAX 64

int main() {
    char original_hostname[HOST_NAME_MAX + 1];

    if (gethostname(original_hostname, sizeof(original_hostname)) == -1) {
        return 1;
    }

    size_t len = strlen(original_hostname);

    int result = syscall(SYS_sethostname, original_hostname, len);

    if (result == -1) {
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "sethostname_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_sethostname_tests()
