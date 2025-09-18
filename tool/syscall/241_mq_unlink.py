
import os

def generate_mq_unlink_tests():
    output_dir = "./tool/cfiles/241_mq_unlink"
    os.makedirs(output_dir, exist_ok=True)

    c_code = r"""#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <mqueue.h>

#ifndef SYS_mq_open
#define SYS_mq_open   240
#endif
#ifndef SYS_mq_unlink
#define SYS_mq_unlink 241
#endif

static int in_this_ns_mqueue_mounted(void) {
    FILE *f = fopen("/proc/self/mountinfo", "re");
    if (!f) return 0;
    char line[1024];
    int found = 0;
    while (fgets(line, sizeof(line), f)) {
        if (strstr(line, " /dev/mqueue ") && strstr(line, " mqueue ")) { found = 1; break; }
    }
    fclose(f);
    return found;
}

static void dump_quick_diag(const char *where) {
    struct stat st;
    fprintf(stderr, "[diag] at %s: uid=%u euid=%u\n", where, (unsigned)getuid(), (unsigned)geteuid());
}

int main(void) {
    char mq_name[64];

    long ur = syscall(SYS_mq_unlink, mq_name);
    if (ur == -1) {
        fprintf(stderr, "[syscall] mq_unlink(%s) before-create: %s (%d)\n", mq_name, strerror(errno), errno);
    }

    struct mq_attr attr;
    attr.mq_flags = 0;
    attr.mq_maxmsg = 10;
    attr.mq_msgsize = 8192;
    attr.mq_curmsgs = 0;

    long mqd_sys = syscall(SYS_mq_open, mq_name, O_CREAT | O_EXCL | O_RDWR, 0600, &attr);
    if (mqd_sys == -1) {
        int e = errno;
        dump_quick_diag("after syscall mq_open fail");

        mqd_t mqd_lib = mq_open(mq_name, O_CREAT | O_EXCL | O_RDWR, 0600, &attr);
        if (mqd_lib == (mqd_t)-1) {
            return 1;
        }

        close((int)mqd_lib);
        if (mq_unlink(mq_name) == -1) {\
            return 1;
        }
        return 0;
    }

    if (close((int)mqd_sys) == -1) {
        syscall(SYS_mq_unlink, mq_name);
        return 1;
    }
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
