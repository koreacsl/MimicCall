
import os

def generate_sched_getscheduler_tests():
    output_dir = "./tool/cfiles/145_sched_getscheduler"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sched.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_sched_getscheduler
#define SYS_sched_getscheduler 145
#endif

int main() {
    pid_t pid = getpid();

    if (syscall(SYS_sched_getscheduler, pid) == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "sched_getscheduler_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_sched_getscheduler_tests()
