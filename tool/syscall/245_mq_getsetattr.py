# -*- coding: utf-8 -*-
import os

def generate_mq_getsetattr_tests():
    output_dir = "./tool/cfiles/245_mq_getsetattr"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <fcntl.h>
#include <sys/stat.h>
#include <mqueue.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <string.h>

#ifndef SYS_mq_open
#define SYS_mq_open 240
#endif
#ifndef SYS_mq_unlink
#define SYS_mq_unlink 241
#endif
#ifndef SYS_mq_getsetattr
#define SYS_mq_getsetattr 245
#endif

int main() {
    const char *mq_name = "/test_mq_getsetattr";
    mqd_t mqd;
    struct mq_attr initial_attr, new_attr, old_attr;

    memset(&initial_attr, 0, sizeof(initial_attr));
    initial_attr.mq_maxmsg = 10;
    initial_attr.mq_msgsize = 8192;

    mqd = mq_open(mq_name, O_CREAT | O_RDWR, 0644, &initial_attr);
    if (mqd == (mqd_t)-1) {
        return 1;
    }

    memset(&new_attr, 0, sizeof(new_attr));
    new_attr.mq_flags = O_NONBLOCK;

    if (syscall(SYS_mq_getsetattr, mqd, &new_attr, &old_attr) == -1) {
        close(mqd);
        mq_unlink(mq_name);
        return 1;
    }

    close(mqd);
    mq_unlink(mq_name);

    return 0;
}
"""
    filename = os.path.join(output_dir, "mq_getsetattr_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_mq_getsetattr_tests()
