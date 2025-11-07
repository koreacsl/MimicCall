
import os

def generate_sched_getattr_tests():
    output_dir = "./tool/cfiles/315_sched_getattr"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/types.h>
#include <string.h>

#ifndef SYS_sched_getattr
#define SYS_sched_getattr 315
#endif

struct sched_attr {
    __u32 size;
    __u32 sched_policy;
    __u64 sched_flags;
    __s32 sched_nice;
    __u32 sched_priority;
    __u64 sched_runtime;
    __u64 sched_deadline;
    __u64 sched_period;
};

int main() {
    struct sched_attr attr;
    memset(&attr, 0, sizeof(attr));
    attr.size = sizeof(attr);

    if (syscall(SYS_sched_getattr, 0, &attr, sizeof(attr), 0) == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "sched_getattr_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_sched_getattr_tests()
