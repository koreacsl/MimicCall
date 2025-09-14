# -*- coding: utf-8 -*-
import os

def generate_mq_timedreceive_tests():
    output_dir = "./tool/cfiles/243_mq_timedreceive"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <fcntl.h>
#include <sys/stat.h>
#include <mqueue.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <time.h>
#include <string.h>

#ifndef SYS_mq_open
#define SYS_mq_open 240
#endif
#ifndef SYS_mq_timedsend
#define SYS_mq_timedsend 242
#endif
#ifndef SYS_mq_timedreceive
#define SYS_mq_timedreceive 243
#endif
#ifndef SYS_mq_unlink
#define SYS_mq_unlink 241
#endif

int main() {
    const char *mq_name = "/test_mq_timedreceive";
    mqd_t mqd;
    struct timespec timeout;
    char message[] = "test message";
    char buffer[128];

    mqd = mq_open(mq_name, O_CREAT | O_RDWR, 0644, NULL);
    if (mqd == (mqd_t)-1) {
        return 1;
    }

    // Send a message first so there is something to receive.
    clock_gettime(CLOCK_REALTIME, &timeout);
    timeout.tv_sec += 1;
    if (syscall(SYS_mq_timedsend, mqd, message, strlen(message), 0, &timeout) == -1) {
        close(mqd);
        mq_unlink(mq_name);
        return 1;
    }

    // Now, try to receive it.
    clock_gettime(CLOCK_REALTIME, &timeout);
    timeout.tv_sec += 1;
    if (syscall(SYS_mq_timedreceive, mqd, buffer, sizeof(buffer), NULL, &timeout) == -1) {
        close(mqd);
        mq_unlink(mq_name);
        return 1;
    }

    close(mqd);
    mq_unlink(mq_name);
    return 0;
}
"""
    filename = os.path.join(output_dir, "mq_timedreceive_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_mq_timedreceive_tests()
