import os

def generate_execve_test():
    output_dir = "./tool/cfiles/59_execve"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>
#include <errno.h>

#ifndef SYS_execve
#define SYS_execve 59
#endif

int main() {
    char *argv[] = {"/bin/true", NULL};
    char *envp[] = {NULL};

    syscall(SYS_execve, "/bin/true", argv, envp);

    return 1;
}
"""
    filename = os.path.join(output_dir, "execve_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_execve_test()
