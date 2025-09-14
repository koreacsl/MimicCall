# -*- coding: utf-8 -*-
import os

def generate_readahead_tests():
    output_dir = "./tool/cfiles/readahead"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_readahead
#define SYS_readahead 187
#endif

#define FILE_SIZE (1024 * 4) // 4KB

int main() {
    const char *path = "/tmp/test_readahead_file";
    int fd = -1;
    char buffer[FILE_SIZE] = {0};

    // Create a temporary file and write some data to it.
    fd = open(path, O_CREAT | O_RDWR, 0644);
    if (fd == -1) {
        return 1;
    }
    if (write(fd, buffer, sizeof(buffer)) != sizeof(buffer)) {
        close(fd);
        unlink(path);
        return 1;
    }

    // Call readahead to populate the page cache for the file.
    // This operation is safe and does not modify the file content.
    if (syscall(SYS_readahead, fd, 0, FILE_SIZE) == -1) {
        close(fd);
        unlink(path);
        return 1;
    }

    // Clean up.
    close(fd);
    unlink(path);

    return 0;
}
"""
    filename = os.path.join(output_dir, "test_readahead.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_readahead_tests()
