import os

output_dir = "./tool/cfiles/429_move_mount"
os.makedirs(output_dir, exist_ok=True)

move_mount_flags = {
    "MOVE_MOUNT_F_SYMLINKS": 1,
    "MOVE_MOUNT_F_AUTOMOUNTS": 2,
    "MOVE_MOUNT_F_EMPTY_PATH": 4,
    "MOVE_MOUNT_T_SYMLINKS": 16,
    "MOVE_MOUNT_T_AUTOMOUNTS": 32,
    "MOVE_MOUNT_T_EMPTY_PATH": 64,
    "MOVE_MOUNT_SET_GROUP": 256,
    "MOVE_MOUNT_BENEATH": 512
}

common_headers = """\
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <stdint.h>
#include <sys/syscall.h>

#ifndef SYS_move_mount
#define SYS_move_mount 429
#endif
"""

define_lines = "\n".join([f"#define {k} {v}" for k, v in move_mount_flags.items()])

def write_c_file(name, code):
    with open(os.path.join(output_dir, f"{name}.c"), "w") as f:
        f.write(code)

def generate_move_mount_tests():
    for flag in move_mount_flags:
        name = f"move_mount_flag_{flag.lower()}"
        code = f"""{common_headers}
{define_lines}

int main() {{
    syscall(SYS_move_mount, -1, "from", -1, "to", {flag});
    return 0;
}}
"""
        write_c_file(name, code)

generate_move_mount_tests()
