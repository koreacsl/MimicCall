# -*- coding: utf-8 -*-
import os

def generate_mq_open_tests():
    output_dir = "./tool/cfiles/240_mq_open"
    os.makedirs(output_dir, exist_ok=True)

    flags = {
        "O_RDONLY": "O_RDONLY",
        "O_WRONLY": "O_WRONLY",
        "O_RDWR": "O_RDWR",
        "O_CREAT_RDONLY": "O_CREAT | O_RDONLY",
        "O_CREAT_WRONLY": "O_CREAT | O_WRONLY",
        "O_CREAT_RDWR": "O_CREAT | O_RDWR",
        "O_CREAT_EXCL": "O_CREAT | O_EXCL"
    }

    modes = {
        "0600": "S_IRUSR | S_IWUSR",
        "0644": "S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH"
    }

    for flag_name, flag_value in flags.items():
        c_code = f"""#include <fcntl.h>
#include <sys/stat.h>
#include <mqueue.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_mq_open
#define SYS_mq_open 240
#endif
#ifndef SYS_mq_unlink
#define SYS_mq_unlink 241
#endif

int main() {{
    const char *mq_name = "/mq_{flag_name}";
    struct mq_attr attr;
    attr.mq_flags = 0;
    attr.mq_maxmsg = 10;
    attr.mq_msgsize = 8192;
    mqd_t mqd;

    mqd = syscall(SYS_mq_open, mq_name, {flag_value}, S_IRUSR | S_IWUSR, &attr);
    if (mqd != (mqd_t)-1) {{
        close(mqd);
    }}

    syscall(SYS_mq_unlink, mq_name);

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"mq_open_{flag_name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_mq_open_tests()
