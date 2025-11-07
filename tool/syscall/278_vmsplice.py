
import os

def generate_vmsplice_tests():
    output_dir = "./tool/cfiles/278_vmsplice"
    os.makedirs(output_dir, exist_ok=True)

    splice_flags = {
        "none": "0",
        "move": "SPLICE_F_MOVE",
        "nonblock": "SPLICE_F_NONBLOCK",
        "more": "SPLICE_F_MORE",
        "gift": "SPLICE_F_GIFT"
    }

    for flag_name, flag_value in splice_flags.items():
        c_code = f"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <sys/uio.h>
#include <sys/syscall.h>

#ifndef SYS_vmsplice
#define SYS_vmsplice 278
#endif

#ifndef SPLICE_F_MOVE
#define SPLICE_F_MOVE 1
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
    int pipefd[2];
    if (pipe(pipefd) == -1) return 1;

    char message[] = "vmsplice!";
    struct iovec iov = {{
        .iov_base = message,
        .iov_len = sizeof(message)
    }};

    syscall(SYS_vmsplice, pipefd[1], &iov, 1, {flag_value});

    close(pipefd[0]);
    close(pipefd[1]);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"vmsplice_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_vmsplice_tests()
