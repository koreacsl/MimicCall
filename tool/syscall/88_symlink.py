
import os

def generate_symlink_tests():
    output_dir = "./tool/cfiles/88_symlink"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_symlink
#define SYS_symlink 88
#endif

int main() {
    const char* target = "/tmp/symlink_test_target";
    const char* linkpath = "/tmp/symlink_test_link";

    unlink(target);
    unlink(linkpath);

    int fd = open(target, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        return 1;
    }
    close(fd);

    if (syscall(SYS_symlink, target, linkpath) == -1) {
        unlink(target);
        return 1;
    }

    unlink(target);
    unlink(linkpath);
    
    return 0;
}
"""
    filename = os.path.join(output_dir, "symlink_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_symlink_tests()
