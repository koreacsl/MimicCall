
import os

def generate_flistxattr_tests():
    output_dir = "./tool/cfiles/196_flistxattr"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/xattr.h>

#ifndef SYS_flistxattr
#define SYS_flistxattr 196
#endif

int main() {
    const char *path = "/tmp/test_flistxattr_file";
    char buffer[128];

    int fd = open(path, O_CREAT | O_RDWR, 0644);
    if (fd == -1) return 1;
    fsetxattr(fd, "user.test1", "v1", 2, 0);

    syscall(SYS_flistxattr, fd, buffer, sizeof(buffer));
    
    close(fd);
    unlink(path);
    return 0;
}
"""
    filename = os.path.join(output_dir, "flistxattr_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_flistxattr_tests()
