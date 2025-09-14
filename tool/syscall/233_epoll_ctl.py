# -*- coding: utf-8 -*-
import os

def generate_epoll_ctl_tests():
    output_dir = "./tool/cfiles/233_epoll_ctl"
    os.makedirs(output_dir, exist_ok=True)

    ops = {
        "ADD": "EPOLL_CTL_ADD",
        "MOD": "EPOLL_CTL_MOD",
        "DEL": "EPOLL_CTL_DEL"
    }
    
    events = ["EPOLLIN", "EPOLLOUT", "EPOLLET", "EPOLLONESHOT"]

    for op_name in ["ADD", "MOD"]:
        op_value = ops[op_name]
        for event_flag in events:
            setup_code = ""
            if op_name == "MOD":
                setup_code = """
    struct epoll_event add_ev;
    add_ev.events = EPOLLIN;
    add_ev.data.fd = fd;
    syscall(SYS_epoll_ctl, epfd, EPOLL_CTL_ADD, fd, &add_ev);"""

            c_code = f"""#include <unistd.h>
#include <sys/syscall.h>
#include <sys/epoll.h>
#include <fcntl.h>

#ifndef SYS_epoll_create1
#define SYS_epoll_create1 291
#endif
#ifndef SYS_epoll_ctl
#define SYS_epoll_ctl 233
#endif

int main() {{
    int epfd = syscall(SYS_epoll_create1, 0);
    if (epfd == -1) return 1;

    int fd = open("/dev/null", O_RDONLY);
    if (fd == -1) {{
        close(epfd);
        return 1;
    }}
    {setup_code}

    struct epoll_event ev;
    ev.events = {event_flag};
    ev.data.fd = fd;

    syscall(SYS_epoll_ctl, epfd, {op_value}, fd, &ev);

    close(fd);
    close(epfd);
    return 0;
}}
"""
            filename = os.path.join(output_dir, f"epoll_ctl_{op_name.lower()}_{event_flag.lower()}.c")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(c_code)

    c_code_del = """#include <unistd.h>
#include <sys/syscall.h>
#include <sys/epoll.h>
#include <fcntl.h>

#ifndef SYS_epoll_create1
#define SYS_epoll_create1 291
#endif
#ifndef SYS_epoll_ctl
#define SYS_epoll_ctl 233
#endif

int main() {
    int epfd = syscall(SYS_epoll_create1, 0);
    if (epfd == -1) return 1;

    int fd = open("/dev/null", O_RDONLY);
    if (fd == -1) {
        close(epfd);
        return 1;
    }

    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = fd;
    syscall(SYS_epoll_ctl, epfd, EPOLL_CTL_ADD, fd, &ev);

    syscall(SYS_epoll_ctl, epfd, EPOLL_CTL_DEL, fd, NULL);

    close(fd);
    close(epfd);
    return 0;
}
"""
    filename_del = os.path.join(output_dir, "epoll_ctl_del.c")
    with open(filename_del, "w", encoding="utf-8") as f:
        f.write(c_code_del)

if __name__ == "__main__":
    generate_epoll_ctl_tests()

