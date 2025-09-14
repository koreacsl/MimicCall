import os
from itertools import combinations

output_dir = "./tool/cfiles/277_sync_file_range"
os.makedirs(output_dir, exist_ok=True)

header = '''#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>
#include <sys/syscall.h>

#ifndef SYS_sync_file_range
#define SYS_sync_file_range 277
#endif

#define SYNC_FILE_RANGE_WAIT_BEFORE 1
#define SYNC_FILE_RANGE_WRITE       2
#define SYNC_FILE_RANGE_WAIT_AFTER  4
'''

flags = {
    "wait_before": "SYNC_FILE_RANGE_WAIT_BEFORE",
    "write": "SYNC_FILE_RANGE_WRITE",
    "wait_after": "SYNC_FILE_RANGE_WAIT_AFTER"
}
flag_items = list(flags.items())

def write_test(name, flag_expr):
    code = f"""{header}
int main() {{
    int fd = open("/dev/null", O_WRONLY);
    if (fd < 0) return 1;
    syscall(SYS_sync_file_range, fd, 0, 4096, {flag_expr});
    close(fd);
    return 0;
}}
"""
    with open(os.path.join(output_dir, f"sync_file_range_flag_{name}.c"), "w") as f:
        f.write(code)

for i in range(1, len(flag_items)+1):
    for combo in combinations(flag_items, i):
        name = "_".join(k for k, _ in combo)
        expr = " | ".join(v for _, v in combo)
        write_test(name, expr)
