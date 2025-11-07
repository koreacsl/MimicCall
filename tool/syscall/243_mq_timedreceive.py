
import os

def generate_mq_timedreceive_tests():
    output_dir = "./tool/cfiles/243_mq_timedreceive"
    os.makedirs(output_dir, exist_ok=True)

    c_code = r"""#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/stat.h>
#include <mqueue.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <time.h>
#include <string.h>
#include <stdio.h>

#ifndef SYS_mq_open
#define SYS_mq_open        240
#endif
#ifndef SYS_mq_timedsend
#define SYS_mq_timedsend   242
#endif
#ifndef SYS_mq_timedreceive
#define SYS_mq_timedreceive 243
#endif
#ifndef SYS_mq_unlink
#define SYS_mq_unlink      241
#endif

int main(void) {
    char mq_name[64];
    snprintf(mq_name, sizeof(mq_name), "/test_mq_timedreceive_%u", (unsigned)getpid());

    mq_unlink(mq_name);

    char buffer[128];
    struct mq_attr attr;
    attr.mq_flags = 0;
    attr.mq_maxmsg = 10;
    attr.mq_msgsize = sizeof(buffer);
    attr.mq_curmsgs = 0;

    mqd_t mqd = mq_open(mq_name, O_CREAT | O_EXCL | O_RDWR, 0644, &attr);
    if (mqd == (mqd_t)-1) {
        return 1;
    }

    const char *message = "test message";
    struct timespec timeout;
    clock_gettime(CLOCK_REALTIME, &timeout);
    timeout.tv_sec += 1;

    if (syscall(SYS_mq_timedsend, mqd, message, strlen(message), 0, &timeout) == -1) {
        close(mqd);
        mq_unlink(mq_name);
        return 1;
    }

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
