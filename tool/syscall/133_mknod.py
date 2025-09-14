# -*- coding: utf-8 -*-
import os

def generate_mknod_tests():
    output_dir = "./tool/cfiles/133_mknod"
    os.makedirs(output_dir, exist_ok=True)

    mknod_modes = ["S_IFIFO", "S_IFCHR", "S_IFBLK", "S_IFREG", "S_IFSOCK"]

    for mode_str in mknod_modes:
        c_code = f"""#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_mknod
#define SYS_mknod 133
#endif

int main() {{
    const char *path = "/tmp/testfile_mknod_{mode_str.lower()}";
    
    // The call might fail for non-root users (e.g., creating device files),
    // which is an expected and safe outcome.
    syscall(SYS_mknod, path, {mode_str} | S_IRUSR | S_IWUSR, 0);

    unlink(path);
    
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"mknod_{mode_str.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_mknod_tests()
