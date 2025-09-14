import os

def generate_dup3_tests():
    output_dir = "./tool/cfiles/dup3"
    os.makedirs(output_dir, exist_ok=True)

    dup3_flags = {
        "0": "0",
        "O_CLOEXEC": "O_CLOEXEC"
    }

    for flag_name, flag_value in dup3_flags.items():
        c_code = f"""#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_dup3
#define SYS_dup3 292
#endif

int main() {{
    int oldfd = open("/dev/null", O_RDONLY);
    if (oldfd == -1) {{
        return 1;
    }}

    int newfd = syscall(SYS_dup3, oldfd, 100, {flag_value});
    if (newfd == -1) {{
        close(oldfd);
        return 1;
    }}

    close(oldfd);
    close(newfd);

    return 0;
}}
"""
        filename = f"{output_dir}/dup3_{flag_name.lower()}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_dup3_tests()
