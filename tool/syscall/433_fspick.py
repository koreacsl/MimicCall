
import os

def generate_fspick_tests():
    output_dir = "./tool/cfiles/433_fspick"
    os.makedirs(output_dir, exist_ok=True)

    fspick_flags = {"none": "0", "cloexec": "FSPICK_CLOEXEC", "empty_path": "AT_EMPTY_PATH"}

    for flag_name, flag_value in fspick_flags.items():
        c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/mount.h>

#ifndef SYS_fspick
#define SYS_fspick 433
#endif

#ifndef O_PATH
#define O_PATH 0x200000
#endif

#ifndef AT_EMPTY_PATH
#define AT_EMPTY_PATH 0x1000
#endif

int main(void) {{
    int dirfd = open("/tmp", O_PATH | O_DIRECTORY, 0);
    if (dirfd < 0) return 1;

    const char* path = ({flag_value} & AT_EMPTY_PATH) ? "" : ".";

    int fd = syscall(SYS_fspick, dirfd, path, {flag_value});
    if (fd >= 0) {{
        close(fd);
    }}

    close(dirfd);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"fspick_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_fspick_tests()
