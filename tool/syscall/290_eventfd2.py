# -*- coding: utf-8 -*-
import os

def generate_eventfd2_tests():
    output_dir = "./tool/cfiles/290_eventfd2"
    os.makedirs(output_dir, exist_ok=True)

    flags = {
        "none": "0",
        "cloexec": "EFD_CLOEXEC",
        "nonblock": "EFD_NONBLOCK",
        "semaphore": "EFD_SEMAPHORE"
    }

    for flag_name, flag_value in flags.items():
        c_code = f"""#include <unistd.h>
#include <sys/syscall.h>
#include <sys/eventfd.h>

#ifndef SYS_eventfd2
#define SYS_eventfd2 290
#endif

int main() {{
    unsigned int initval = 0;
    
    int fd = syscall(SYS_eventfd2, initval, {flag_value});
    if (fd == -1) {{
        return 1;
    }}

    close(fd);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"eventfd2_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_eventfd2_tests()
