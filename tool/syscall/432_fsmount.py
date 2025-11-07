
import os

def generate_fsmount_tests():
    output_dir = "./tool/cfiles/432_fsmount"
    os.makedirs(output_dir, exist_ok=True)

    fsmount_flags = {"none": "0", "cloexec": "FSMOUNT_CLOEXEC"}
    mount_attr_flags = {"rdonly": "MOUNT_ATTR_RDONLY", "nosuid": "MOUNT_ATTR_NOSUID"}

    for fsmount_name, fsmount_value in fsmount_flags.items():
        for attr_name, attr_value in mount_attr_flags.items():
            c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/mount.h>

#ifndef SYS_fsopen
#define SYS_fsopen 430
#endif
#ifndef SYS_fsconfig
#define SYS_fsconfig 431
#endif
#ifndef SYS_fsmount
#define SYS_fsmount 432
#endif

int main() {{
    int fd = syscall(SYS_fsopen, "tmpfs", 0);
    if (fd < 0) return 1;

    syscall(SYS_fsconfig, fd, FSCONFIG_CMD_CREATE, NULL, NULL, 0);

    int mfd = syscall(SYS_fsmount, fd, {fsmount_value}, {attr_value});
    if (mfd >= 0) {{
        close(mfd);
    }}

    close(fd);
    return 0;
}}
"""
            filename = os.path.join(output_dir, f"fsmount_{fsmount_name}_{attr_name}.c")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_fsmount_tests()
