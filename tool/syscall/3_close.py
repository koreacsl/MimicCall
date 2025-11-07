import os

def generate_close_test():
    output_dir = "./tool/cfiles/3_close"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

int main() {
    int fd = open("/dev/null", O_RDONLY);
    if (fd == -1) {
        return 1;
    }

    if (syscall(SYS_close, fd) == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = f"{output_dir}/close_0.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_close_test()

