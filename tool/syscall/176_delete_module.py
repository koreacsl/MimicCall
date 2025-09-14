# -*- coding: utf-8 -*-
import os

def generate_delete_module_tests():
    output_dir = "./tool/cfiles/176_delete_module"
    os.makedirs(output_dir, exist_ok=True)
    
    delete_module_flags = {
        "O_NONBLOCK": 0x00004000,
        "O_TRUNC": 0x00000200
    }

    for flag_name, flag_value in delete_module_flags.items():
        c_code = f"""#include <unistd.h>
#include <sys/syscall.h>
#include <fcntl.h>

#ifndef SYS_delete_module
#define SYS_delete_module 176
#endif

int main() {{
    const char *module_name = "non_existent_module";

    syscall(SYS_delete_module, module_name, {flag_name});

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"delete_module_{flag_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_delete_module_tests()
