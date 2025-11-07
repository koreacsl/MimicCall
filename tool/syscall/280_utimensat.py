
import os

def generate_utimensat_tests():
    output_dir = "./tool/cfiles/280_utimensat"
    os.makedirs(output_dir, exist_ok=True)
    
    flags = {
        "none": "0",
        "symlink_nofollow": "AT_SYMLINK_NOFOLLOW"
    }

    for flag_name, flag_value in flags.items():
        c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_utimensat
#define SYS_utimensat 280
#endif

#ifndef AT_SYMLINK_NOFOLLOW
#define AT_SYMLINK_NOFOLLOW 0x100
#endif

int main() {{
    const char *filename = "testfile_utimensat";
    const char *path = "/tmp/testfile_utimensat";
    
    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {{
        return 1;
    }}
    close(fd);

    int dirfd = open("/tmp", O_RDONLY | O_DIRECTORY);
    if (dirfd == -1) {{
        unlink(path);
        return 1;
    }}

    if (syscall(SYS_utimensat, dirfd, filename, NULL, {flag_value}) == -1) {{
        close(dirfd);
        unlink(path);
        return 1;
    }}
    
    close(dirfd);
    unlink(path);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"utimensat_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_utimensat_tests()

