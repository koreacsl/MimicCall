
import os

def generate_epoll_create_tests():
    output_dir = "./tool/cfiles/213_epoll_create"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_epoll_create
#define SYS_epoll_create 213
#endif

int main() {
    int epfd = syscall(SYS_epoll_create, 1);
    if (epfd == -1) {
        return 1;
    }

    close(epfd);
    return 0;
}
"""
    filename = os.path.join(output_dir, "epoll_create_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_epoll_create_tests()
