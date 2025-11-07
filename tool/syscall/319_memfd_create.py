import os
import itertools

def generate_memfd_create_tests():
    output_dir = "./tool/cfiles/319_memfd_create"
    os.makedirs(output_dir, exist_ok=True)

    memfd_flags = [
        "MFD_CLOEXEC",
        "MFD_ALLOW_SEALING",
        "MFD_HUGETLB"
    ]

    huge_page_flags = [
        "MFD_HUGE_64KB",
        "MFD_HUGE_512KB",
        "MFD_HUGE_1MB",
        "MFD_HUGE_2MB"
    ]

    for r in range(1, len(memfd_flags) + 1):
        for flag_combination in itertools.combinations(memfd_flags, r):
            flags_str = " | ".join(flag_combination)
            flag_name = "_".join([flag.lower() for flag in flag_combination])
            syscall_name = f"memfd_create_{flag_name}"
            
            c_code = f"""#define _GNU_SOURCE
#include <sys/mman.h>
#include <linux/memfd.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <fcntl.h>

int main() {{
    int fd = syscall(SYS_memfd_create, "test_memfd", {flags_str});
    if (fd == -1) return 1;
    close(fd);
    return 0;
}}
"""
            filename = f"{output_dir}/{syscall_name}.c"
            with open(filename, "w") as f:
                f.write(c_code)

    for huge_flag in huge_page_flags:
        syscall_name = f"memfd_create_{huge_flag.lower()}"
        
        c_code = f"""#define _GNU_SOURCE
#include <sys/mman.h>
#include <linux/memfd.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <fcntl.h>

int main() {{
    int fd = syscall(SYS_memfd_create, "test_memfd", MFD_HUGETLB | {huge_flag});
    if (fd == -1) return 1;
    close(fd);
    return 0;
}}
"""
        filename = f"{output_dir}/{syscall_name}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_memfd_create_tests()
