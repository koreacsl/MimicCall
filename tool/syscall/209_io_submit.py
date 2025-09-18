
import os

def generate_io_submit_tests():
    output_dir = "./tool/cfiles/209_io_submit"
    os.makedirs(output_dir, exist_ok=True)

    lio_opcodes = [
        "IOCB_CMD_PREAD", "IOCB_CMD_PWRITE", "IOCB_CMD_FSYNC",
        "IOCB_CMD_FDSYNC", "IOCB_CMD_NOOP"
    ]
    iocb_flags = ["0", "IOCB_FLAG_RESFD"]

    for opcode in lio_opcodes:
        for flag in iocb_flags:
            c_code = f"""#include <unistd.h>
#include <sys/syscall.h>
#include <linux/aio_abi.h>
#include <string.h>
#include <fcntl.h>

#ifndef SYS_io_setup
#define SYS_io_setup 206
#endif
#ifndef SYS_io_destroy
#define SYS_io_destroy 207
#endif
#ifndef SYS_io_submit
#define SYS_io_submit 209
#endif

int main() {{
    aio_context_t ctx = 0;
    struct iocb cb;
    struct iocb *cbs[1];
    const char* path = "/tmp/io_submit_test_file";

    if (syscall(SYS_io_setup, 1, &ctx) < 0) return 1;

    int fd = open(path, O_CREAT | O_RDWR, 0644);
    if (fd == -1) {{
        syscall(SYS_io_destroy, ctx);
        return 1;
    }}

    memset(&cb, 0, sizeof(cb));
    cb.aio_fildes = fd;
    cb.aio_lio_opcode = {opcode};
    cb.aio_flags = {flag};
    cbs[0] = &cb;

    syscall(SYS_io_submit, ctx, 1, cbs);
    
    syscall(SYS_io_destroy, ctx);
    close(fd);
    unlink(path);

    return 0;
}}
"""
            filename = os.path.join(output_dir, f"io_submit_{opcode.lower()}_{flag.lower()}.c")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_io_submit_tests()
