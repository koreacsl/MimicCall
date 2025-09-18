
import os

def generate_readlinkat_tests():
    output_dir = "./tool/cfiles/267_readlinkat"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_readlinkat
#define SYS_readlinkat 267
#endif

int main() {
    const char* target = "/tmp/readlinkat_test_target";
    const char* linkname = "readlinkat_test_link";
    const char* linkpath = "/tmp/readlinkat_test_link";
    char buf[1024];

    unlink(target);
    unlink(linkpath);

    int fd = open(target, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        return 1;
    }
    close(fd);

    if (symlink(target, linkpath) == -1) {
        unlink(target);
        return 1;
    }

    int dirfd = open("/tmp", O_RDONLY | O_DIRECTORY);
    if (dirfd == -1) {
        unlink(target);
        unlink(linkpath);
        return 1;
    }

    if (syscall(SYS_readlinkat, dirfd, linkname, buf, sizeof(buf) - 1) == -1) {
        close(dirfd);
        unlink(target);
        unlink(linkpath);
        return 1;
    }
    
    close(dirfd);
    unlink(target);
    unlink(linkpath);

    return 0;
}
"""
    filename = os.path.join(output_dir, "readlinkat_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_readlinkat_tests()
