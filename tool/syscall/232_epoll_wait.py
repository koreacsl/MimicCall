
import os

def generate_epoll_wait_tests():
    output_dir = "./tool/cfiles/232_epoll_wait"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>
#include <sys/epoll.h>

#ifndef SYS_epoll_create1
#define SYS_epoll_create1 291
#endif
#ifndef SYS_epoll_wait
#define SYS_epoll_wait 232
#endif

int main() {
    int epfd = syscall(SYS_epoll_create1, 0);
    if (epfd == -1) return 1;

    struct epoll_event events[1];
    
    syscall(SYS_epoll_wait, epfd, events, 1, 1);

    close(epfd);
    return 0;
}
"""
    filename = os.path.join(output_dir, "epoll_wait_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_epoll_wait_tests()
