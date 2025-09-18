
import os

def generate_epoll_pwait_tests():
    output_dir = "./tool/cfiles/281_epoll_pwait"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>
#include <sys/epoll.h>
#include <signal.h>
#include <time.h>

#ifndef SYS_epoll_create1
#define SYS_epoll_create1 291
#endif
#ifndef SYS_epoll_pwait
#define SYS_epoll_pwait 281
#endif

int main() {
    int epfd = syscall(SYS_epoll_create1, 0);
    if (epfd == -1) return 1;

    struct epoll_event events[1];
    struct timespec timeout = { .tv_sec = 0, .tv_nsec = 1000000 };
    sigset_t sigmask;
    sigemptyset(&sigmask);

    syscall(SYS_epoll_pwait, epfd, events, 1, &timeout, &sigmask, sizeof(sigset_t));

    close(epfd);
    return 0;
}
"""
    filename = os.path.join(output_dir, "epoll_pwait_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_epoll_pwait_tests()
