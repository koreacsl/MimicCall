import os

def generate_fallocate_tests():
    output_dir = "./tool/cfiles/285_fallocate"

    fallocate_modes = [
        ("fallocate_keep_size", "FALLOC_FL_KEEP_SIZE"),
        ("fallocate_punch_hole", "FALLOC_FL_PUNCH_HOLE"),
        ("fallocate_collapse_range", "FALLOC_FL_COLLAPSE_RANGE"),
        ("fallocate_zero_range", "FALLOC_FL_ZERO_RANGE"),
        ("fallocate_insert_range", "FALLOC_FL_INSERT_RANGE"),
        ("fallocate_unshare_range", "FALLOC_FL_UNSHARE_RANGE"),
        ("fallocate_no_hide_stale", "FALLOC_FL_NO_HIDE_STALE"),
    ]

    for syscall_name, mode in fallocate_modes:
        c_code = f"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

int main() {{
    int fd = open("testfile", O_CREAT | O_RDWR, 0644);
    if (fd == -1) return 1;

    int result = syscall(SYS_fallocate, fd, {mode}, 0, 4096);
    
    close(fd);
    unlink("testfile");
    return result;
}}
"""
        filename = f"{output_dir}/{syscall_name}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    output_dir = "./tool/cfiles/fallocate"
    os.makedirs(output_dir, exist_ok=True)
    generate_fallocate_tests()
