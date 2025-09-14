# -*- coding: utf-8 -*-
import os

def generate_umount2_tests():
    output_dir = "./tool/cfiles/166_umount2"
    os.makedirs(output_dir, exist_ok=True)

    flags = {
        "MNT_FORCE": 1,
        "MNT_DETACH": 2,
        "MNT_EXPIRE": 4,
        "UMOUNT_NOFOLLOW": 8
    }

    for flag_name, flag_value in flags.items():
        c_code = f"""#include <sys/mount.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/stat.h>
#include <fcntl.h>

#ifndef SYS_mount
#define SYS_mount 165
#endif
#ifndef SYS_umount2
#define SYS_umount2 166
#endif

#ifndef {flag_name}
#define {flag_name} {flag_value}
#endif

int main() {{
    const char *tgt = "/tmp/umount2_tgt_root_{flag_name.lower()}";
    int mount_result = -1;
    int umount_result = -1;

    rmdir(tgt);

    if (mkdir(tgt, 0755) != 0) {{
        return 1;
    }}

    mount_result = syscall(SYS_mount, "tmpfs", tgt, "tmpfs", 0, NULL);
    if (mount_result != 0) {{
        rmdir(tgt);
        return 1;
    }}

    umount_result = syscall(SYS_umount2, tgt, {flag_name});

    rmdir(tgt);

    if (mount_result == 0 && umount_result == 0) {{
        return 0;
    }}

    return 1;
}}
"""
        filename = os.path.join(output_dir, f"umount2_{flag_name.lower()}_root.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_umount2_tests()

