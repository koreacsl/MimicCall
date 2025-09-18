
import os

def generate_inotify_init1_tests():
    output_dir = "./tool/cfiles/294_inotify_init1"
    os.makedirs(output_dir, exist_ok=True)

    flags = {"none": "0", "nonblock": "IN_NONBLOCK", "cloexec": "IN_CLOEXEC"}
    for flag_name, flag_value in flags.items():
        c_code = f"""#include <unistd.h>
#include <sys/syscall.h>
#include <sys/inotify.h>

#ifndef SYS_inotify_init1
#define SYS_inotify_init1 294
#endif

int main() {{
    int fd = syscall(SYS_inotify_init1, {flag_value});
    if (fd == -1) {{
        return 1;
    }}
    close(fd);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"inotify_init1_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_inotify_init1_tests()
