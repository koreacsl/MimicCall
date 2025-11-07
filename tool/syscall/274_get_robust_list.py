
import os

def generate_get_robust_list_tests():
    output_dir = "./tool/cfiles/274_get_robust_list"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>
#include <stddef.h>

#ifndef SYS_get_robust_list
#define SYS_get_robust_list 274
#endif

struct robust_list_head;

int main() {
    struct robust_list_head *head = NULL;
    size_t len = 0;

    syscall(SYS_get_robust_list, 0, &head, &len);

    return 0;
}
"""
    filename = os.path.join(output_dir, "get_robust_list_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_get_robust_list_tests()
