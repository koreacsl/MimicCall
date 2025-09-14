# -*- coding: utf-8 -*-
import os

def generate_mkdir_tests():
    output_dir = "./tool/cfiles/83_mkdir"
    os.makedirs(output_dir, exist_ok=True)

    open_modes = [
        "S_IRWXU",
        "S_IRUSR_S_IWUSR",
        "S_IRWXG",
        "S_IRWXO",
        "S_IRWXU_S_IRWXG_S_IRWXO"
    ]

    for mode_name in open_modes:
        c_mode_expression = mode_name.replace('_', ' | ')
        c_code = f"""#include <sys/stat.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_mkdir
#define SYS_mkdir 83
#endif

int main() {{
    const char* path = "/tmp/test_mkdir_dir";

    rmdir(path);

    if (syscall(SYS_mkdir, path, {c_mode_expression}) == -1) {{
        return 1;
    }}

    if (rmdir(path) == -1) {{
        return 1;
    }}

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"mkdir_{mode_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_mkdir_tests()

