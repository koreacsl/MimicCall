import os

def generate_sysfs_tests():
    output_dir = "./tool/cfiles/139_sysfs"
    os.makedirs(output_dir, exist_ok=True)
    
    c_code_sysfs_1 = """#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <linux/kdev_t.h>
#include <sys/syscall.h>

int main() {
    const char *fsname = "ext4";
    int result = syscall(SYS_sysfs, 1, fsname);
    
    if (result == -1) return 1;
    
    return 0;
}
"""
    filename = f"{output_dir}/sysfs_1.c"
    with open(filename, "w") as f:
        f.write(c_code_sysfs_1)
    
    c_code_sysfs_2 = """#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <linux/kdev_t.h>
#include <sys/syscall.h>

int main() {
    int fsindex = 1;
    char fsname[32];
    int result = syscall(SYS_sysfs, 2, fsindex, fsname);

    if (result == -1) return 1;

    return 0;
}
"""
    filename = f"{output_dir}/sysfs_2.c"
    with open(filename, "w") as f:
        f.write(c_code_sysfs_2)

    c_code_sysfs_3 = """#include <stdio.h>
#include <unistd.h>
#include <sys/syscall.h>

int main() {
    int result = syscall(SYS_sysfs, 3);
    if (result == -1) return 1;

    return 0;
}
"""
    filename = f"{output_dir}/sysfs_3.c"
    with open(filename, "w") as f:
        f.write(c_code_sysfs_3)

if __name__ == "__main__":
    generate_sysfs_tests()
