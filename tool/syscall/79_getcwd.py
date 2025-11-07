import os

def generate_getcwd_test():
    output_dir = "./tool/cfiles/79_getcwd"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_getcwd
#define SYS_getcwd 79
#endif

int main() {
    char buf[1024];
    long result = syscall(SYS_getcwd, buf, sizeof(buf));
    return (result < 0) ? 1 : 0;
}
"""
    filename = os.path.join(output_dir, "getcwd_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_getcwd_test()
