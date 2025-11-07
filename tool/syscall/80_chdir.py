
import os

def generate_chdir_test():
    output_dir = "./tool/cfiles/80_chdir"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_chdir
#define SYS_chdir 80
#endif

int main() {
    const char *path = "/tmp";
    int result = syscall(SYS_chdir, path);
    return (result == -1) ? 1 : 0;
}
"""
    filename = os.path.join(output_dir, "chdir_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_chdir_test()
