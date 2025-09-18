
import os

def generate_set_robust_list_tests():
    output_dir = "./tool/cfiles/273_set_robust_list"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>
#include <stdint.h>
#include <string.h>

#ifndef SYS_set_robust_list
#define SYS_set_robust_list 273
#endif

struct robust_list {
    struct robust_list *next;
};

struct robust_list_head {
    struct robust_list list;
    long futex_offset;
    struct robust_list *list_op_pending;
};

int main() {
    struct robust_list_head head;
    memset(&head, 0, sizeof(head));

    syscall(SYS_set_robust_list, &head, sizeof(head));

    return 0;
}
"""
    filename = os.path.join(output_dir, "set_robust_list_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_set_robust_list_tests()
