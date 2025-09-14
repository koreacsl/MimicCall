import os

output_dir = "./tool/cfiles/442_mount_setattr"
os.makedirs(output_dir, exist_ok=True)

mount_setattr_flags = [
    "AT_EMPTY_PATH", "AT_NO_AUTOMOUNT", "AT_RECURSIVE", "AT_SYMLINK_NOFOLLOW"
]

mount_attr_flags = {
    "MOUNT_ATTR_IDMAP": 1048576,
    "MOUNT_ATTR_RDONLY": 1,
    "MOUNT_ATTR_NOSUID": 2,
    "MOUNT_ATTR_NODEV": 4,
    "MOUNT_ATTR_NOEXEC": 8,
    "MOUNT_ATTR__ATIME": 112,
    "MOUNT_ATTR_NODIRATIME": 128
}

mount_attr_propagation_flags = {
    "MS_UNBINDABLE": 131072,
    "MS_PRIVATE": 262144,
    "MS_SLAVE": 524288,
    "MS_SHARED": 1048576
}

common_headers = """\
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <stdint.h>
#include <sys/syscall.h>

#ifndef SYS_mount_setattr
#define SYS_mount_setattr 442
#endif
"""

define_lines = "\n".join([f"#define {k} {v}" for k, v in {**mount_attr_flags, **mount_attr_propagation_flags}.items()])

mount_attr_struct = """\
struct mount_attr {
    uint64_t attr_set;
    uint64_t attr_clr;
    uint64_t propagation;
    uint64_t userns_fd;
};
"""

def write_c_file(name, code):
    with open(os.path.join(output_dir, f"{name}.c"), "w") as f:
        f.write(code)

def generate_tests():
    for flag in mount_setattr_flags:
        name = f"mount_setattr_flag_{flag.lower()}"
        code = f"""{common_headers}
{define_lines}
{mount_attr_struct}

int main() {{
    struct mount_attr attr = {{0}};
    syscall(SYS_mount_setattr, -1, "dummy", {flag}, &attr, sizeof(attr));
    return 0;
}}
"""
        write_c_file(name, code)

    for flag in mount_attr_flags:
        write_c_file(
            f"mount_setattr_attr_set_{flag.lower()}",
            f"""{common_headers}
{define_lines}
{mount_attr_struct}

int main() {{
    struct mount_attr attr = {{ .attr_set = {flag} }};
    syscall(SYS_mount_setattr, -1, "dummy", 0, &attr, sizeof(attr));
    return 0;
}}
""")
        write_c_file(
            f"mount_setattr_attr_clr_{flag.lower()}",
            f"""{common_headers}
{define_lines}
{mount_attr_struct}

int main() {{
    struct mount_attr attr = {{ .attr_clr = {flag} }};
    syscall(SYS_mount_setattr, -1, "dummy", 0, &attr, sizeof(attr));
    return 0;
}}
""")

    for flag in mount_attr_propagation_flags:
        name = f"mount_setattr_propagation_{flag.lower()}"
        code = f"""{common_headers}
{define_lines}
{mount_attr_struct}

int main() {{
    struct mount_attr attr = {{ .propagation = {flag} }};
    syscall(SYS_mount_setattr, -1, "dummy", 0, &attr, sizeof(attr));
    return 0;
}}
"""
        write_c_file(name, code)

generate_tests()
