# -*- coding: utf-8 -*-
import os

def generate_seccomp_tests():
    output_dir = "./tool/cfiles/317_seccomp"
    os.makedirs(output_dir, exist_ok=True)

    common_headers = """#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/prctl.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <string.h>
#include <stddef.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/bpf.h>

#ifndef SYS_seccomp
#define SYS_seccomp 317
#endif
"""

    c_code_strict = f"""{common_headers}
int main() {{
    syscall(SYS_prctl, PR_SET_SECCOMP, SECCOMP_MODE_STRICT);
    syscall(SYS_exit, 0);
    return 1;
}}
"""
    with open(os.path.join(output_dir, "test_mode_strict.c"), "w", encoding="utf-8") as f:
        f.write(c_code_strict)

    c_code_filter = f"""{common_headers}
int main() {{
    struct sock_filter filter[] = {{
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    }};
    struct sock_fprog prog = {{
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    }};
    
    if (syscall(SYS_prctl, PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {{
        return 1;
    }}

    // This test is safe because the filter explicitly allows all syscalls.
    if (syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) == -1) {{
        return 1;
    }}
    return 0;
}}
"""
    with open(os.path.join(output_dir, "test_mode_filter.c"), "w", encoding="utf-8") as f:
        f.write(c_code_filter)

    c_code_info = f"""{common_headers}
int main() {{
    // Test GET_ACTION_AVAIL
    unsigned int action = SECCOMP_RET_LOG;
    syscall(SYS_seccomp, SECCOMP_GET_ACTION_AVAIL, 0, &action);

    // Test GET_NOTIF_SIZES
    struct seccomp_notif_sizes sizes;
    syscall(SYS_seccomp, SECCOMP_GET_NOTIF_SIZES, 0, &sizes);

    return 0;
}}
"""
    with open(os.path.join(output_dir, "test_get_info.c"), "w", encoding="utf-8") as f:
        f.write(c_code_info)

    c_code_listener = f"""{common_headers}
int main() {{
    struct sock_filter filter[] = {{
        // A simple filter that traps an unlikely syscall to create a listener.
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_getpgid, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_TRAP),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    }};
    struct sock_fprog prog = {{
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    }};
    int listener_fd;
    
    syscall(SYS_prctl, PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);

    listener_fd = syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, SECCOMP_FILTER_FLAG_NEW_LISTENER, &prog);
    if (listener_fd == -1) {{
        return 0;
    }}

    struct seccomp_notif notif;
    ioctl(listener_fd, SECCOMP_IOCTL_NOTIF_RECV, &notif);

    struct seccomp_notif_resp resp;
    memset(&resp, 0, sizeof(resp));
    resp.id = 0; // Dummy ID
    ioctl(listener_fd, SECCOMP_IOCTL_NOTIF_SEND, &resp);

    unsigned long long dummy_id = 0;
    ioctl(listener_fd, SECCOMP_IOCTL_NOTIF_ID_VALID, &dummy_id);

    close(listener_fd);
    return 0;
}}
"""
    with open(os.path.join(output_dir, "test_listener_and_ioctls.c"), "w", encoding="utf-8") as f:
        f.write(c_code_listener)


if __name__ == "__main__":
    generate_seccomp_tests()
