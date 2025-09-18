
import os

def generate_io_getevents_tests():
    output_dir = "./tool/cfiles/208_io_getevents"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>
#include <linux/aio_abi.h>
#include <time.h>

#ifndef SYS_io_setup
#define SYS_io_setup 206
#endif
#ifndef SYS_io_destroy
#define SYS_io_destroy 207
#endif
#ifndef SYS_io_getevents
#define SYS_io_getevents 208
#endif

int main() {
    aio_context_t ctx = 0;
    struct io_event events[1];
    struct timespec timeout = { .tv_sec = 0, .tv_nsec = 1000000 };

    if (syscall(SYS_io_setup, 1, &ctx) < 0) {
        return 1;
    }

    syscall(SYS_io_getevents, ctx, 0, 1, events, &timeout);

    syscall(SYS_io_destroy, ctx);

    return 0;
}
"""
    filename = os.path.join(output_dir, "io_getevents_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_io_getevents_tests()
