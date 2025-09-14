import os

def generate_pipe2_tests():
    output_dir = "./tool/cfiles/293_pipe2"
    os.makedirs(output_dir, exist_ok=True)

    pipe_flags = {
        "0": "none",
        "O_NONBLOCK": "nonblock",
        "O_CLOEXEC": "cloexec",
        "O_DIRECT": "direct"
    }

    for flag, name in pipe_flags.items():
        c_code = f"""#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_pipe2
#define SYS_pipe2 293
#endif

int main() {{
    int pipefd[2];

    if (syscall(SYS_pipe2, pipefd, {flag}) == -1) {{
        return 1;
    }}

    close(pipefd[0]);
    close(pipefd[1]);

    return 0;
}}
"""
        filename = f"{output_dir}/pipe2_{name}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_pipe2_tests()
