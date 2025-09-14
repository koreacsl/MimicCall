import os

def generate_pipe_test():
    output_dir = "./tool/cfiles/22_pipe"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_pipe
#define SYS_pipe 22
#endif

int main() {
    int pipefd[2];

    if (syscall(SYS_pipe, pipefd) == -1) {
        return 1;
    }

    close(pipefd[0]);
    close(pipefd[1]);
    
    return 0;
}
"""
    filename = f"{output_dir}/pipe_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_pipe_test()
