# -*- coding: utf-8 -*-
import os

def generate_faccessat_tests():
    output_dir = "./tool/cfiles/269_faccessat"
    os.makedirs(output_dir, exist_ok=True)

    open_modes = {
        "read": "R_OK",
        "write": "W_OK",
        "exec": "X_OK"
    }

    for mode_name, mode_value in open_modes.items():
        c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_faccessat
#define SYS_faccessat 269
#endif

int main() {{
    const char *path = "/tmp/test_faccessat_file";
    
    int fd = open(path, O_CREAT | O_WRONLY, 0755);
    if (fd == -1) return 1;
    close(fd);

    syscall(SYS_faccessat, AT_FDCWD, path, {mode_value}, 0);

    unlink(path);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"faccessat_{mode_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_faccessat_tests()
