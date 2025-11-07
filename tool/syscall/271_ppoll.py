import os

def generate_ppoll_tests():
    output_dir = "./tool/cfiles/271_ppoll"
    os.makedirs(output_dir, exist_ok=True)

    pollfd_events = [
        "POLLIN", "POLLPRI", "POLLOUT", "POLLERR", "POLLHUP", "POLLNVAL",
        "POLLRDNORM", "POLLRDBAND", "POLLWRNORM", "POLLWRBAND"
    ]

    for event in pollfd_events:
        c_code = f"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <signal.h>
#include <time.h>
#include <sys/syscall.h>

#ifndef SYS_ppoll
#define SYS_ppoll 271
#endif

#ifndef POLLFREE
#define POLLFREE 16384
#endif

#ifndef POLLREMOVE
#define POLLREMOVE 4096
#endif

#ifndef POLLRDHUP
#define POLLRDHUP 16
#endif

#ifndef POLLMSG
#define POLLMSG 1024
#endif

int main() {{
    int fd = open("/dev/null", O_RDWR);
    if (fd == -1) return 1;

    struct pollfd fds[1];
    fds[0].fd = fd;
    fds[0].events = {event};

    struct timespec timeout = {{0, 1000000}};
    int result = syscall(SYS_ppoll, fds, 1, &timeout, NULL);

    close(fd);
    return (result >= 0) ? 0 : 1;
}}
"""
        filename = f"{output_dir}/ppoll_{event.lower()}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_ppoll_tests()