
import os

def generate_sched_setparam_tests():
    output_dir = "./tool/cfiles/142_sched_setparam"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sched.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_sched_setparam
#define SYS_sched_setparam 142
#endif
#ifndef SYS_sched_getparam
#define SYS_sched_getparam 143
#endif

int main() {
    pid_t pid = getpid();
    struct sched_param orig_param;

    if (syscall(SYS_sched_getparam, pid, &orig_param) == -1) {
        return 0;
    }

    struct sched_param new_param = { .sched_priority = orig_param.sched_priority };
    
    syscall(SYS_sched_setparam, pid, &new_param);

    syscall(SYS_sched_setparam, pid, &orig_param);

    return 0;
}
"""
    filename = os.path.join(output_dir, "sched_setparam_safe.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_sched_setparam_tests()
