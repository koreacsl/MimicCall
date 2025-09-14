# -*- coding: utf-8 -*-
import os

def generate_mq_unlink_tests():
    output_dir = "./tool/cfiles/241_mq_unlink"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <fcntl.h>
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

int main() {
    const char *mq_name = "/test_mq_to_unlink";
    mqd_t mqd;

    mqd = mq_open(mq_name, O_CREAT | O_RDWR, 0644, NULL);
    if (mqd == (mqd_t)-1) {
        syscall(SYS_mq_unlink, mq_name);
        return 0;
    }
    close(mqd);

    if (syscall(SYS_mq_unlink, mq_name) == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "mq_unlink_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_mq_unlink_tests()
