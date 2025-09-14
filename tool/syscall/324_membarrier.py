import os

def generate_membarrier_tests():
    output_dir = "./tool/cfiles/324_membarrier"
    os.makedirs(output_dir, exist_ok=True)

    membarrier_cmds = [
        "MEMBARRIER_CMD_GLOBAL",
        "MEMBARRIER_CMD_GLOBAL_EXPEDITED",
        "MEMBARRIER_CMD_PRIVATE_EXPEDITED",
        "MEMBARRIER_CMD_REGISTER_PRIVATE_EXPEDITED",
        "MEMBARRIER_CMD_PRIVATE_EXPEDITED_SYNC_CORE",
        "MEMBARRIER_CMD_REGISTER_PRIVATE_EXPEDITED_SYNC_CORE",
        "MEMBARRIER_CMD_QUERY",
        "MEMBARRIER_CMD_REGISTER_GLOBAL_EXPEDITED",
        "MEMBARRIER_CMD_SHARED"
    ]

    for cmd in membarrier_cmds:
        syscall_name = f"membarrier_{cmd.lower()}"
        c_code = f"""#define _GNU_SOURCE
#include <linux/membarrier.h>
#include <sys/syscall.h>
#include <unistd.h>

int main() {{
    int result = syscall(SYS_membarrier, {cmd}, 0);
    return result == -1 ? 1 : 0;
}}
"""
        filename = f"{output_dir}/{syscall_name}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_membarrier_tests()
