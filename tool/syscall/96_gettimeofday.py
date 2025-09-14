import os

def generate_gettimeofday_tests():
    output_dir = "./tool/cfiles/96_gettimeofday"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <sys/time.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_gettimeofday
#define SYS_gettimeofday 96
#endif

int main() {
    struct timeval tv;
    struct timezone tz;

    if (syscall(SYS_gettimeofday, &tv, &tz) == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = os.path.join(output_dir, "gettimeofday_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_gettimeofday_tests()