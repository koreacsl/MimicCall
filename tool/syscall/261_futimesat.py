
import os

def generate_futimesat_test():
    output_dir = "./tool/cfiles/261_futimesat"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/time.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_futimesat
#define SYS_futimesat 261
#endif

int main() {
    const char *filename = "testfile_futimesat";
    const char *path = "/tmp/testfile_futimesat";
    
    int fd = open(path, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        return 1;
    }
    close(fd);

    int dirfd = open("/tmp", O_RDONLY | O_DIRECTORY);
    if (dirfd == -1) {
        unlink(path);
        return 1;
    }

    if (syscall(SYS_futimesat, dirfd, filename, NULL) == -1) {
        close(dirfd);
        unlink(path);
        return 1;
    }
    
    close(dirfd);
    unlink(path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "futimesat_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_futimesat_test()
