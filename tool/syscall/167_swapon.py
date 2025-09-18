
import os

def generate_swapon_tests():
    output_dir = "./tool/cfiles/167_swapon"
    os.makedirs(output_dir, exist_ok=True)

    flags = {
        "none": "0",
        "prefer": "0x8000",   # SWAP_FLAG_PREFER
        "discard": "0x10000"  # SWAP_FLAG_DISCARD
    }

    for flag_name, flag_value in flags.items():
        c_code = f"""#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

#ifndef SYS_swapon
#define SYS_swapon 167
#endif
#ifndef SYS_swapoff
#define SYS_swapoff 168
#endif

#define SWAP_FILE_SIZE (1024 * 1024)

int main(void) {{
    const char *path = "/tmp/tmpswapfile_root_{flag_name}";
    int fd = -1;
    int swapon_result = -1;
    int swapoff_result = -1;

    fd = open(path, O_CREAT | O_RDWR, 0600);
    if (fd == -1) {{
        perror("open");
        return 1;
    }}

    int rc = posix_fallocate(fd, 0, SWAP_FILE_SIZE);
    if (rc != 0) {{
        errno = rc;
        perror("posix_fallocate");
        close(fd);
        unlink(path);
        return 1;
    }}
    close(fd);

    rc = system("/sbin/mkswap -f /tmp/tmpswapfile_root_{flag_name}");
    if (rc != 0) {{
        rc = system("mkswap -f /tmp/tmpswapfile_root_{flag_name}");
        if (rc != 0) {{
            fprintf(stderr, "mkswap failed (rc=%d)\\n", rc);
            unlink(path);
            return 1;
        }}
    }}

    swapon_result = syscall(SYS_swapon, path, {flag_value});
    if (swapon_result != 0) {{
        perror("swapon");
        unlink(path);
        return 1;
    }}

    swapoff_result = syscall(SYS_swapoff, path);
    if (swapoff_result != 0) {{
        perror("swapoff");
        unlink(path);
        return 1;
    }}

    unlink(path);

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"swapon_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_swapon_tests()
