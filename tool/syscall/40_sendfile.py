# -*- coding: utf-8 -*-
import os

def generate_sendfile_tests():
    output_dir = "./tool/cfiles/40_sendfile"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>
#include <sys/sendfile.h>
#include <fcntl.h>

#ifndef SYS_sendfile
#define SYS_sendfile 40
#endif

int main() {
    const char *in_path = "/tmp/sendfile_test_in";
    int in_fd, out_fd;
    char buffer[] = "hello sendfile";

    in_fd = open(in_path, O_CREAT | O_RDWR, 0644);
    if (in_fd == -1) {
        return 1;
    }
    write(in_fd, buffer, sizeof(buffer));
    lseek(in_fd, 0, SEEK_SET);

    out_fd = open("/dev/null", O_WRONLY);
    if (out_fd == -1) {
        close(in_fd);
        unlink(in_path);
        return 1;
    }

    if (syscall(SYS_sendfile, out_fd, in_fd, NULL, sizeof(buffer)) == -1) {
        close(in_fd);
        close(out_fd);
        unlink(in_path);
        return 1;
    }

    close(in_fd);
    close(out_fd);
    unlink(in_path);

    return 0;
}
"""
    filename = os.path.join(output_dir, "sendfile_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_sendfile_tests()
