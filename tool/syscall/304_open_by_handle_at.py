# -*- coding: utf-8 -*-
import os

def generate_open_by_handle_at_tests():
    output_dir = "./tool/cfiles/304_open_by_handle_at"
    os.makedirs(output_dir, exist_ok=True)

    open_flags = {
        "o_rdonly": "O_RDONLY",
        "o_wronly": "O_WRONLY",
        "o_rdwr": "O_RDWR",
        "o_append": "O_APPEND",
        "o_cloexec": "O_CLOEXEC",
        "o_direct": "O_DIRECT",
        "o_dsync": "O_DSYNC",
        "o_largefile": "O_LARGEFILE",
        "o_noatime": "O_NOATIME",
        "o_nonblock": "O_NONBLOCK",
        "o_path": "O_PATH",
        "o_sync": "O_SYNC",
        "o_trunc": "O_TRUNC" # This flag should be ignored by the syscall
    }

    for flag_name, flag_value in open_flags.items():
        c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <string.h>

#ifndef SYS_name_to_handle_at
#define SYS_name_to_handle_at 303
#endif
#ifndef SYS_open_by_handle_at
#define SYS_open_by_handle_at 304
#endif

// Some flags might not be defined in older headers
#ifndef O_PATH
#define O_PATH 010000000
#endif

struct file_handle {{
    unsigned int handle_bytes;
    int handle_type;
    char f_handle[0];
}};

int main() {{
    const char *path = "/tmp/test_open_by_handle_file";
    char handle_buf[128];
    struct file_handle *fhp = (struct file_handle*)handle_buf;
    int mount_id, mount_fd, opened_fd;

    int tmp_fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (tmp_fd == -1) return 1;
    close(tmp_fd);

    mount_fd = open("/tmp", O_RDONLY | O_DIRECTORY);
    if (mount_fd == -1) {{
        unlink(path);
        return 1;
    }}

    fhp->handle_bytes = sizeof(handle_buf) - sizeof(*fhp);
    if (syscall(SYS_name_to_handle_at, mount_fd, "test_open_by_handle_file", fhp, &mount_id, 0) == -1) {{
        close(mount_fd);
        unlink(path);
        return 1; // Can't test open_by_handle_at if we can't get a handle.
    }}

    opened_fd = syscall(SYS_open_by_handle_at, mount_fd, fhp, {flag_value});
    if (opened_fd != -1) {{
        close(opened_fd);
    }}

    close(mount_fd);
    unlink(path);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"open_by_handle_at_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_open_by_handle_at_tests()

