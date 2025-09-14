# -*- coding: utf-8 -*-
import os

def generate_process_vm_readv_tests():
    output_dir = "./tool/cfiles/310_process_vm_readv"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/uio.h>
#include <sys/wait.h>
#include <string.h>
#include <stdlib.h>

#ifndef SYS_process_vm_readv
#define SYS_process_vm_readv 310
#endif

int main() {
    char local_buffer[32];
    char child_buffer[32];
    strcpy(child_buffer, "hello from child");

    struct iovec local_iov = { .iov_base = local_buffer, .iov_len = sizeof(local_buffer) };
    struct iovec remote_iov = { .iov_base = child_buffer, .iov_len = sizeof(child_buffer) };
    pid_t pid = getpid();
    ssize_t result;

    result = syscall(SYS_process_vm_readv, pid, &local_iov, 1, &remote_iov, 1, 0);

    return (result > 0 && strcmp(local_buffer, "hello from child") == 0) ? 0 : 1;
}
"""
    filename = os.path.join(output_dir, "process_vm_readv.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_process_vm_readv_tests()
