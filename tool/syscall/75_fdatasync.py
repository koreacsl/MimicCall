import os

def generate_fdatasync_tests():
    output_dir = "./tool/cfiles/75_fdatasync"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_fdatasync
#define SYS_fdatasync 75
#endif

int main() {
    int fd = open("/dev/null", O_WRONLY);
    if (fd == -1) {
        return 1;
    }

    int result = syscall(SYS_fdatasync, fd);
    
    close(fd);

    return (result == -1) ? 1 : 0;
}
"""
    filename = os.path.join(output_dir, "fdatasync_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_fdatasync_tests()
