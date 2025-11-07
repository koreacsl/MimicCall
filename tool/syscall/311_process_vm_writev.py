
import os

def generate_process_vm_writev_tests():
    output_dir = "./tool/cfiles/311_process_vm_writev"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/uio.h>
#include <sys/wait.h>
#include <string.h>
#include <stdlib.h>

#ifndef SYS_process_vm_writev
#define SYS_process_vm_writev 311
#endif

int main() {
    char local_buffer[32];
    char child_buffer[32] = {0};
    strcpy(local_buffer, "hello from parent");

    struct iovec local_iov = { .iov_base = local_buffer, .iov_len = sizeof(local_buffer) };
    struct iovec remote_iov = { .iov_base = child_buffer, .iov_len = sizeof(child_buffer) };
    pid_t pid = getpid();
    ssize_t result;

    result = syscall(SYS_process_vm_writev, pid, &local_iov, 1, &remote_iov, 1, 0);

    return (result > 0 && strcmp(child_buffer, "hello from parent") == 0) ? 0 : 1;
}
"""
    filename = os.path.join(output_dir, "process_vm_writev.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_process_vm_writev_tests()
