import os

output_dir = "./tool/cfiles/428_open_tree"
os.makedirs(output_dir, exist_ok=True)

open_tree_flags = [
    "AT_EMPTY_PATH", "AT_NO_AUTOMOUNT", "AT_RECURSIVE",
    "AT_SYMLINK_NOFOLLOW", "OPEN_TREE_CLONE", "OPEN_TREE_CLOEXEC"
]

common_headers = """\
#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <stdint.h>

#ifndef SYS_open_tree
#define SYS_open_tree 428
#endif

#define OPEN_TREE_CLOEXEC 524288
#define OPEN_TREE_CLONE 1
"""

def write_c_file(name, code):
    with open(os.path.join(output_dir, f"{name}.c"), "w") as f:
        f.write(code)

def generate_open_tree_tests():
    for flag in open_tree_flags:
        name = f"open_tree_flag_{flag.lower()}"
        code = f"""{common_headers}

int main() {{
    syscall(SYS_open_tree, AT_FDCWD, ".", {flag});
    return 0;
}}
"""
        write_c_file(name, code)

generate_open_tree_tests()
