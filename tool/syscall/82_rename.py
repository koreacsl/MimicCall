import os

def generate_rename_test():
    output_dir = "./tool/cfiles/82_rename"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_rename
#define SYS_rename 82
#endif

int main() {
    const char* old_path = "/tmp/testfile_rename_old";
    const char* new_path = "/tmp/testfile_rename_new";

    remove(old_path);
    remove(new_path);

    int fd_old = open(old_path, O_RDWR | O_CREAT, 0666);
    if (fd_old == -1) {
        return 1;
    }
    close(fd_old);

    if (syscall(SYS_rename, old_path, new_path) == -1) {
        remove(old_path);
        return 1;
    }

    remove(new_path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "rename_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_rename_test()
