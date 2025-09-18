
import os

def generate_tee_tests():
    output_dir = "./tool/cfiles/276_tee"
    os.makedirs(output_dir, exist_ok=True)

    splice_flags = {
        "none": "0",
        "nonblock": "SPLICE_F_NONBLOCK",
        "more": "SPLICE_F_MORE",
        "gift": "SPLICE_F_GIFT"
    }

    for flag_name, flag_value in splice_flags.items():
        c_code = f"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_tee
#define SYS_tee 276
#endif

#ifndef SPLICE_F_NONBLOCK
#define SPLICE_F_NONBLOCK 2
#endif
#ifndef SPLICE_F_MORE
#define SPLICE_F_MORE 4
#endif
#ifndef SPLICE_F_GIFT
#define SPLICE_F_GIFT 8
#endif

int main() {{
    int pipefd1[2], pipefd2[2];
    if (pipe(pipefd1) == -1 || pipe(pipefd2) == -1) return 1;

    if (write(pipefd1[1], "hello", 5) != 5) {{
        close(pipefd1[0]); close(pipefd1[1]);
        close(pipefd2[0]); close(pipefd2[1]);
        return 1;
    }}

    syscall(SYS_tee, pipefd1[0], pipefd2[1], 5, {flag_value});

    close(pipefd1[0]);
    close(pipefd1[1]);
    close(pipefd2[0]);
    close(pipefd2[1]);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"tee_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_tee_tests()
