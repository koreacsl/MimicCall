import os

def generate_ustat_test():
    output_dir = "./tool/cfiles/136_ustat"
    os.makedirs(output_dir, exist_ok=True)

    c_code = f"""#define _GNU_SOURCE
#include <sys/syscall.h>
#include <unistd.h>
#include <stdio.h>
#include <linux/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdlib.h>
#include <sys/sysmacros.h>
#include <sys/vfs.h>
#include <errno.h>

struct ustat {{
    __kernel_daddr_t f_tfree;
    __kernel_ino_t f_tinode;
    char f_fname[6];
    char f_fpack[6];
}};

int main() {{
    const char *path = "/tmp";
    struct stat statbuf;
    
    if (stat(path, &statbuf) == -1) return 1;

    int major_num = major(statbuf.st_dev);
    int minor_num = minor(statbuf.st_dev);

    dev_t dev_num = makedev(major_num, minor_num);
    
    struct ustat fs_info;

    int result = syscall(SYS_ustat, dev_num, &fs_info);
    if (result == -1) {{
        if (errno == EINVAL) {{
            return 0;
        }} else {{
            return 1;
        }}
    }}

    return 0;
}}
"""

    filename = f"{output_dir}/ustat_0.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_ustat_test()
