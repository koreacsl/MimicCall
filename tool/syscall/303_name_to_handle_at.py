# -*- coding: utf-8 -*-
import os

def generate_name_to_handle_at_tests():
    output_dir = "./tool/cfiles/303_name_to_handle_at"
    os.makedirs(output_dir, exist_ok=True)

    handle_flags = {
        "none": "0",
        "empty_path": "AT_EMPTY_PATH",
        "symlink_follow": "AT_SYMLINK_FOLLOW"
    }

    for flag_name, flag_value in handle_flags.items():
        c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <string.h>

#ifndef SYS_name_to_handle_at
#define SYS_name_to_handle_at 303
#endif

#ifndef AT_EMPTY_PATH
#define AT_EMPTY_PATH 0x1000
#endif
#ifndef AT_SYMLINK_FOLLOW
#define AT_SYMLINK_FOLLOW 0x400
#endif

struct file_handle {{
    unsigned int handle_bytes;
    int handle_type;
    char f_handle[0];
}};

int main() {{
    const char *path = "/tmp/test_handle_file";
    // Using a large buffer for the handle.
    char handle_buf[128];
    struct file_handle *fhp = (struct file_handle*)handle_buf;
    int mount_id;

    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) return 1;
    close(fd);

    int dirfd = open("/tmp", O_RDONLY | O_DIRECTORY);
    if (dirfd == -1) {{
        unlink(path);
        return 1;
    }}

    fhp->handle_bytes = sizeof(handle_buf) - sizeof(*fhp);

    // This may fail without sufficient privileges, which is a safe outcome.
    syscall(SYS_name_to_handle_at, dirfd, "test_handle_file", fhp, &mount_id, {flag_value});

    close(dirfd);
    unlink(path);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"name_to_handle_at_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_name_to_handle_at_tests()
