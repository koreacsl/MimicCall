import os

def generate_msync_tests():
    output_dir = "./tool/cfiles/26_msync"
    os.makedirs(output_dir, exist_ok=True)

    msync_flags = {
        "ms_async": "MS_ASYNC",
        "ms_sync": "MS_SYNC",
        "ms_invalidate": "MS_INVALIDATE"
    }

    for flag_name, flag_value in msync_flags.items():
        syscall_name = f"msync_{flag_name}"
        
        c_code = f"""#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <sys/syscall.h>

int main() {{
    int fd = open("testfile", O_RDWR | O_CREAT, 0666);
    if (fd == -1) return 1;

    write(fd, "Testing msync function.", 23);

    void *addr = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (addr == MAP_FAILED) {{
        close(fd);
        return 1;
    }}

    strcpy((char *)addr, "Modified by msync.");

    if (syscall(SYS_msync, addr, 4096, {flag_value}) == -1) {{
        munmap(addr, 4096);
        close(fd);
        return 1;
    }}

    munmap(addr, 4096);
    close(fd);

    unlink("testfile");
    return 0;
}}
"""
        
        filename = f"{output_dir}/{syscall_name}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_msync_tests()
