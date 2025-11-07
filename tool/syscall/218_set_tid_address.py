import os

def generate_set_tid_address_tests():
    output_dir = "./tool/cfiles/218_set_tid_address"
    os.makedirs(output_dir, exist_ok=True)
    
    c_code = f"""#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <stdio.h>

int main() {{
    int tid_storage = 0;
    int tid = syscall(SYS_set_tid_address, &tid_storage);

    if (tid == -1) return 1;

    return 0;
}}
"""
    filename = f"{output_dir}/set_tid_address_0.c"
    with open(filename, "w") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_set_tid_address_tests()
