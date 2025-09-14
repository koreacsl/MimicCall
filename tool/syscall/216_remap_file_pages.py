import os

def generate_remap_file_pages_tests():
    output_dir = "./tool/cfiles/216_remap_file_pages"
    os.makedirs(output_dir, exist_ok=True)

    mmap_flags = [
        "MAP_SHARED",
        "MAP_PRIVATE",
    ]

    mmap_prots = [
        "PROT_READ | PROT_WRITE",
    ]

    for prot in mmap_prots:
        for flag in mmap_flags:
            syscall_name = f"remap_file_pages_{prot.lower().replace(' | ', '_')}_{flag.lower()}"
            c_code = f"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <errno.h>

int main() {{
    int page_size = sysconf(_SC_PAGESIZE);
    int fd = open("/tmp/testfile", O_RDWR | O_CREAT | O_TRUNC, 0666);
    if (fd == -1) {{
        perror("open");
        return 1;
    }}

    if (ftruncate(fd, page_size * 2) == -1) {{
        perror("ftruncate");
        close(fd);
        return 1;
    }}

    void *addr = mmap(NULL, page_size * 2, {prot}, {flag}, fd, 0);
    if (addr == MAP_FAILED) {{
        perror("mmap");
        close(fd);
        return 1;
    }}

    char *ptr = (char*)addr;
    ptr[0] = 'A';
    ptr[page_size] = 'B';

    for (int i = 0; i < 2; i++) {{
        void *page_addr = (char*)addr + i * page_size;
        if (syscall(SYS_remap_file_pages, page_addr, page_size, 0, 0, 0) == -1) {{
            if (errno == ENOSYS) {{
                fprintf(stderr, "remap_file_pages not implemented on this system\\n");
            }} else {{
                perror("remap_file_pages");
            }}
            munmap(addr, page_size * 2);
            close(fd);
            unlink("/tmp/testfile");
            return 1;
        }}
    }}

    if (munmap(addr, page_size * 2) == -1) {{
        perror("munmap");
        close(fd);
        unlink("/tmp/testfile");
        return 1;
    }}

    close(fd);
    unlink("/tmp/testfile");

    return 0;
}}
"""
            filename = f"{output_dir}/{syscall_name}.c"
            with open(filename, "w") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_remap_file_pages_tests()
