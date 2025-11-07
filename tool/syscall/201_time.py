
import os

def generate_time_tests():
    output_dir = "./tool/cfiles/201_time"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_time
#define SYS_time 201
#endif

int main() {
    if (syscall(SYS_time, NULL) == -1) {
        return 1;
    }
    return 0;
}
"""
    filename = os.path.join(output_dir, "time_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_time_tests()
