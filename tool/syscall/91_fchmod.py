# -*- coding: utf-8 -*-
import os

def generate_fchmod_tests():
    output_dir = "./tool/cfiles/91_fchmod"
    os.makedirs(output_dir, exist_ok=True)

    modes = {
        "0755": "S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH",
        "0644": "S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH",
        "0700": "S_IRWXU"
    }

    for mode_name, mode_flags in modes.items():
        c_code = f"""#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_fchmod
#define SYS_fchmod 91
#endif

int main() {{
    const char* path = "/tmp/fchmod_test_file";

    unlink(path);

    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {{
        return 1;
    }}

    if (syscall(SYS_fchmod, fd, {mode_flags}) == -1) {{
        close(fd);
        unlink(path);
        return 1;
    }}

    close(fd);

    if (unlink(path) == -1) {{
        return 1;
    }}

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"fchmod_{mode_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_fchmod_tests()
