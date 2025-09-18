import os

def generate_process_madvise_tests():
    output_dir = "./tool/cfiles/440_process_madvise"
    os.makedirs(output_dir, exist_ok=True)

    madvise_flags = {
        "MADV_NORMAL": 0, "MADV_RANDOM": 1, "MADV_SEQUENTIAL": 2, "MADV_WILLNEED": 3, "MADV_DONTNEED": 4,
        "MADV_REMOVE": 9, "MADV_DONTFORK": 10, "MADV_DOFORK": 11, "MADV_MERGEABLE": 12, "MADV_UNMERGEABLE": 13,
        "MADV_HUGEPAGE": 14, "MADV_NOHUGEPAGE": 15, "MADV_DONTDUMP": 16, "MADV_DODUMP": 17, "MADV_WIPEONFORK": 18,
        "MADV_KEEPONFORK": 19, "MADV_COLD": 20, "MADV_PAGEOUT": 21, "MADV_POPULATE_READ": 22, "MADV_POPULATE_WRITE": 23,
        "MADV_HWPOISON": 100, "MADV_SOFT_OFFLINE": 101
    }

    for flag_name, flag_value in madvise_flags.items():
        c_code = f"""#define _GNU_SOURCE
#include <sys/mman.h>
#include <sys/uio.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <errno.h>
#include <stdio.h>

#ifndef SYS_process_madvise
#define SYS_process_madvise 440
#endif

#ifndef SYS_pidfd_open
#define SYS_pidfd_open 434
#endif

#ifndef {flag_name}
#define {flag_name} {flag_value}
#endif

int main(void) {{
    void *addr = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) {{
        perror("mmap");
        return 1;
    }}

    struct iovec vec;
    vec.iov_base = addr;
    vec.iov_len = 4096;

    int pidfd = (int)syscall(SYS_pidfd_open, getpid(), 0);
    if (pidfd == -1) {{
        perror("pidfd_open");
        munmap(addr, 4096);
        return 1;
    }}

    long rc = syscall(SYS_process_madvise, pidfd, &vec, 1, {flag_name}, 0);

    int saved_errno = errno;
    close(pidfd);

    if (rc == -1) {{
        munmap(addr, 4096);
        return 1;
    }}

    munmap(addr, 4096);
    return 0;
}}
"""
        filename = f"{output_dir}/process_madvise_{flag_name.lower()}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_process_madvise_tests()
