
import os

def generate_close_range_tests():
    output_dir = "./tool/cfiles/436_close_range"
    os.makedirs(output_dir, exist_ok=True)

    flags = {
        "none": "0",
        "unshare": "CLOSE_RANGE_UNSHARE",
        "cloexec": "CLOSE_RANGE_CLOEXEC"
    }

    for flag_name, flag_value in flags.items():
        c_code = f"""#include <unistd.h>
#include <sys/syscall.h>
#include <fcntl.h>

#ifndef SYS_close_range
#define SYS_close_range 436
#endif

#ifndef CLOSE_RANGE_UNSHARE
#define CLOSE_RANGE_UNSHARE (1U << 1)
#endif
#ifndef CLOSE_RANGE_CLOEXEC
#define CLOSE_RANGE_CLOEXEC (1U << 2)
#endif

int main() {{
    int fd1 = open("/dev/null", O_RDONLY);
    int fd2 = open("/dev/null", O_RDONLY);
    int fd3 = open("/dev/null", O_RDONLY);

    if (fd1 == -1 || fd2 == -1 || fd3 == -1) {{
        if (fd1 != -1) close(fd1);
        if (fd2 != -1) close(fd2);
        if (fd3 != -1) close(fd3);
        return 1;
    }}

    syscall(SYS_close_range, (unsigned int)fd1, (unsigned int)fd3, {flag_value});

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"close_range_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_close_range_tests()
