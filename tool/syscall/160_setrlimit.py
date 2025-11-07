
import os

def generate_setrlimit_tests():
    output_dir = "./tool/cfiles/160_setrlimit"
    os.makedirs(output_dir, exist_ok=True)

    rlimit_types = [
        "RLIMIT_AS", "RLIMIT_CORE", "RLIMIT_CPU", "RLIMIT_DATA",
        "RLIMIT_FSIZE", "RLIMIT_LOCKS", "RLIMIT_MEMLOCK", "RLIMIT_MSGQUEUE",
        "RLIMIT_NICE", "RLIMIT_NOFILE", "RLIMIT_NPROC", "RLIMIT_RSS",
        "RLIMIT_RTPRIO", "RLIMIT_RTTIME", "RLIMIT_SIGPENDING", "RLIMIT_STACK"
    ]

    for rlimit_type in rlimit_types:
        c_code = f"""#include <sys/resource.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef SYS_setrlimit
#define SYS_setrlimit 160
#endif
#ifndef SYS_getrlimit
#define SYS_getrlimit 97
#endif

int main() {{
    struct rlimit old_limit, new_limit;

    if (syscall(SYS_getrlimit, {rlimit_type}, &old_limit) == -1) {{
        return 1;
    }}

    new_limit = old_limit;

    if (syscall(SYS_setrlimit, {rlimit_type}, &new_limit) == -1) {{
    }}

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"setrlimit_{rlimit_type.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_setrlimit_tests()
