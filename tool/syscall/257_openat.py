import os

def generate_openat_tests():
    output_dir = "./tool/cfiles/257_openat"
    os.makedirs(output_dir, exist_ok=True)

    open_flags = [
        "O_WRONLY", "O_RDWR", "O_APPEND", "FASYNC", "O_CLOEXEC", "O_CREAT", "O_DIRECT",
        "O_DIRECTORY", "O_EXCL", "O_LARGEFILE", "O_NOATIME", "O_NOCTTY", "O_NOFOLLOW",
        "O_NONBLOCK", "O_PATH", "O_SYNC", "O_TRUNC", "__O_TMPFILE"
    ]

    for flag in open_flags:
        path = '"/tmp"' if flag == "__O_TMPFILE" else '"/dev/null"'
        base_flags = "O_RDWR"

        if flag == "__O_TMPFILE":
            final_flags = f"{base_flags} | {flag}"
        elif flag == "O_PATH":
            final_flags = flag
        else:
            final_flags = f"{base_flags} | {flag}"

        c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef FASYNC
#define FASYNC 0
#endif

#ifndef __O_TMPFILE
#define __O_TMPFILE 0
#endif

int main() {{
    int fd = syscall(SYS_openat, AT_FDCWD, {path}, {final_flags}, 0644);
    if (fd == -1) {{
        return 1;
    }}
    close(fd);
    return 0;
}}
"""
        filename = f"{output_dir}/openat_{flag.lower()}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_openat_tests()
