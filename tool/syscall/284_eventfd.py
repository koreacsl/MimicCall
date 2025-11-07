
import os

def generate_eventfd_tests():
    output_dir = "./tool/cfiles/284_eventfd"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_eventfd
#define SYS_eventfd 284
#endif

int main() {
    unsigned int initval = 0;
    
    int fd = syscall(SYS_eventfd, initval);
    if (fd == -1) {
        return 1;
    }

    close(fd);
    return 0;
}
"""
    filename = os.path.join(output_dir, "eventfd_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_eventfd_tests()
