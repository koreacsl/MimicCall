import os
from itertools import combinations

userfaultfd_dir = "./tool/cfiles/323_userfaultfd"
os.makedirs(userfaultfd_dir, exist_ok=True)

common_header = '''#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <stdint.h>
#include <sys/syscall.h>
'''

userfaultfd_header = common_header + '''
#ifndef SYS_userfaultfd
#define SYS_userfaultfd 323
#endif

#define UFFD_USER_MODE_ONLY (1 << 4)
'''

flags = {
    "nonblock": "O_NONBLOCK",
    "cloexec": "O_CLOEXEC",
    "user_mode": "UFFD_USER_MODE_ONLY"
}
items = list(flags.items())

for i in range(1, len(items)+1):
    for combo in combinations(items, i):
        name = "_".join(k for k, _ in combo)
        expr = " | ".join(v for _, v in combo)
        fname = f"userfaultfd_flag_{name}.c"
        code = userfaultfd_header + f'''
int main() {{
    syscall(SYS_userfaultfd, {expr});
    return 0;
}}
'''
        with open(os.path.join(userfaultfd_dir, fname), "w") as f:
            f.write(code)
