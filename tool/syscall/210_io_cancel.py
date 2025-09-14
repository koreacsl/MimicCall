# -*- coding: utf-8 -*-
import os

def generate_io_cancel_tests():
    output_dir = "./tool/cfiles/210_io_cancel"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>
#include <linux/aio_abi.h>
#include <string.h>

#ifndef SYS_io_setup
#define SYS_io_setup 206
#endif
#ifndef SYS_io_destroy
#define SYS_io_destroy 207
#endif
#ifndef SYS_io_cancel
#define SYS_io_cancel 210
#endif

int main() {
    aio_context_t ctx = 0;
    struct iocb cb;
    struct io_event res;

    if (syscall(SYS_io_setup, 1, &ctx) < 0) {
        return 1;
    }

    memset(&cb, 0, sizeof(cb));
    
    syscall(SYS_io_cancel, ctx, &cb, &res);

    syscall(SYS_io_destroy, ctx);

    return 0;
}
"""
    filename = os.path.join(output_dir, "io_cancel_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_io_cancel_tests()
