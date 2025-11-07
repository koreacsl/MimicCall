
import os

def generate_epoll_create1_tests():
    output_dir = "./tool/cfiles/291_epoll_create1"
    os.makedirs(output_dir, exist_ok=True)

    flags = {
        "none": "0",
        "cloexec": "EPOLL_CLOEXEC"
    }

    for flag_name, flag_value in flags.items():
        c_code = f"""#include <unistd.h>
#include <sys/syscall.h>
#include <sys/epoll.h>

#ifndef SYS_epoll_create1
#define SYS_epoll_create1 291
#endif

int main() {{
    int epfd = syscall(SYS_epoll_create1, {flag_value});
    if (epfd == -1) {{
        return 1;
    }}

    close(epfd);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"epoll_create1_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_epoll_create1_tests()
