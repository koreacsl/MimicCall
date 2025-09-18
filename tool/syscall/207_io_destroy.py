
import os

def generate_io_destroy_tests():
    output_dir = "./tool/cfiles/207_io_destroy"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>
#include <linux/aio_abi.h>

#ifndef SYS_io_setup
#define SYS_io_setup 206
#endif
#ifndef SYS_io_destroy
#define SYS_io_destroy 207
#endif

int main() {
    aio_context_t ctx = 0;

    if (syscall(SYS_io_setup, 1, &ctx) < 0) {
        return 1;
    }

    if (syscall(SYS_io_destroy, ctx) < 0) {
        return 1;
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "io_destroy_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_io_destroy_tests()
