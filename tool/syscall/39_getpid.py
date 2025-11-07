import os

def generate_getpid_test():
    output_dir = "./tool/cfiles/39_getpid"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>
#include <sys/types.h>

#ifndef SYS_getpid
#define SYS_getpid 39
#endif

int main() {
    pid_t pid = syscall(SYS_getpid);
    if (pid > 0) {
        return 0;
    }
    return 1;
}
"""
    filename = f"{output_dir}/getpid_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_getpid_test()
