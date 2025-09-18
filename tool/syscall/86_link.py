
import os

def generate_link_tests():
    output_dir = "./tool/cfiles/86_link"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_link
#define SYS_link 86
#endif

int main() {
    const char* oldpath = "/tmp/link_test_old";
    const char* newpath = "/tmp/link_test_new";

    unlink(oldpath);
    unlink(newpath);

    int fd = open(oldpath, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        return 1;
    }
    close(fd);

    if (syscall(SYS_link, oldpath, newpath) == -1) {
        unlink(oldpath);
        return 1;
    }

    unlink(oldpath);
    unlink(newpath);
    
    return 0;
}
"""
    filename = os.path.join(output_dir, "link_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_link_tests()
