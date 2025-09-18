
import os

def generate_mknodat_tests():
    output_dir = "./tool/cfiles/259_mknodat"
    os.makedirs(output_dir, exist_ok=True)

    mknod_modes = ["S_IFIFO", "S_IFCHR", "S_IFBLK", "S_IFREG", "S_IFSOCK"]

    for mode_str in mknod_modes:
        dev_expression = "0"
        if mode_str in ["S_IFCHR", "S_IFBLK"]:
            dev_expression = "makedev(1, 3)"

        c_code = f"""#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/sysmacros.h>

#ifndef SYS_mknodat
#define SYS_mknodat 259
#endif

int main() {{
    const char *filename = "testfile_mknodat_{mode_str.lower()}";
    const char *full_path = "/tmp/testfile_mknodat_{mode_str.lower()}";

    int dirfd = open("/tmp", O_RDONLY | O_DIRECTORY);
    if (dirfd == -1) {{
        return 1;
    }}

    syscall(SYS_mknodat, dirfd, filename, {mode_str} | S_IRUSR | S_IWUSR, {dev_expression});
    
    close(dirfd);
    
    unlink(full_path);
    
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"mknodat_{mode_str.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_mknodat_tests()

