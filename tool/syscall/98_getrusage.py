# -*- coding: utf-8 -*-
import os

def generate_getrusage_tests():
    output_dir = "./tool/cfiles/98_getrusage"
    os.makedirs(output_dir, exist_ok=True)

    rusage_whos = [
        ("getrusage_self", "RUSAGE_SELF"),
        ("getrusage_children", "RUSAGE_CHILDREN"),
        ("getrusage_thread", "RUSAGE_THREAD")
    ]

    for syscall_name, who in rusage_whos:
        c_code = f"""#include <sys/resource.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef RUSAGE_THREAD
#define RUSAGE_THREAD 1
#endif

#ifndef SYS_getrusage
#define SYS_getrusage 98
#endif

int main() {{
    struct rusage usage;

    if (syscall(SYS_getrusage, {who}, &usage) == -1) return 1;
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"{syscall_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_getrusage_tests()
