# -*- coding: utf-8 -*-
import os

def generate_fanotify_init_tests():
    output_dir = "./tool/cfiles/300_fanotify_init"
    os.makedirs(output_dir, exist_ok=True)

    fanotify_flags = {
        "CLASS_PRE_CONTENT": "FAN_CLASS_PRE_CONTENT",
        "CLASS_CONTENT": "FAN_CLASS_CONTENT",
        "CLASS_NOTIF": "FAN_CLASS_NOTIF",
        "CLOEXEC": "FAN_CLOEXEC",
        "NONBLOCK": "FAN_NONBLOCK",
        "UNLIMITED_QUEUE": "FAN_UNLIMITED_QUEUE",
        "UNLIMITED_MARKS": "FAN_UNLIMITED_MARKS",
    }

    event_flags = {
        "O_RDONLY": "O_RDONLY",
        "O_WRONLY": "O_WRONLY",
        "O_RDWR": "O_RDWR",
        "O_LARGEFILE": "O_LARGEFILE",
        "O_CLOEXEC": "O_CLOEXEC",
        "O_APPEND": "O_APPEND",
        "O_DSYNC": "O_DSYNC",
        "O_NOATIME": "O_NOATIME",
        "O_NONBLOCK": "O_NONBLOCK",
        "O_SYNC": "O_SYNC"
    }

    for init_name, init_value in fanotify_flags.items():
        for event_name, event_value in event_flags.items():
            c_code = f"""#include <sys/fanotify.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <fcntl.h>

#ifndef SYS_fanotify_init
#define SYS_fanotify_init 300
#endif

int main() {{
    int fd = syscall(SYS_fanotify_init, {init_value}, {event_value});

    if (fd != -1) {{
        close(fd);
    }}

    return 0;
}}
"""
            filename = os.path.join(output_dir, f"fanotify_init_{init_name.lower()}_{event_name.lower()}.c")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_fanotify_init_tests()

