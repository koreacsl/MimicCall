import os
import itertools

output_dir = "./tool/cfiles/250_keyctl"
os.makedirs(output_dir, exist_ok=True)

key_perm_values = {
    "KEY_POS_VIEW": 16777216, "KEY_POS_READ": 33554432, "KEY_POS_WRITE": 67108864,
    "KEY_POS_SEARCH": 134217728, "KEY_POS_LINK": 268435456, "KEY_POS_SETATTR": 536870912,
    "KEY_USR_VIEW": 65536, "KEY_USR_READ": 131072, "KEY_USR_WRITE": 262144,
    "KEY_USR_SEARCH": 524288, "KEY_USR_LINK": 1048576, "KEY_USR_SETATTR": 2097152,
    "KEY_GRP_VIEW": 256, "KEY_GRP_READ": 512, "KEY_GRP_WRITE": 1024,
    "KEY_GRP_SEARCH": 2048, "KEY_GRP_LINK": 4096, "KEY_GRP_SETATTR": 8192,
    "KEY_OTH_VIEW": 1, "KEY_OTH_READ": 2, "KEY_OTH_WRITE": 4,
    "KEY_OTH_SEARCH": 8, "KEY_OTH_LINK": 16, "KEY_OTH_SETATTR": 32
}

common_headers = """\
#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/keyctl.h>
#include <stdint.h>
#include <string.h>

#ifndef SYS_keyctl
#define SYS_keyctl 250
#endif
"""

key_perm_defines = "\n".join([f"#define {k} {v}" for k, v in key_perm_values.items()])

def write_c_file(name, body):
    path = os.path.join(output_dir, f"{name}.c")
    with open(path, "w") as f:
        f.write(body)

def generate_basic_test(cmd_name, body):
    content = f"{common_headers}\n{key_perm_defines}\n\nint main() {{\n    {body}\n    return 0;\n}}\n"
    write_c_file(f"keyctl_{cmd_name.lower()}_basic", content)

def generate_setperm_tests():
    perms = list(key_perm_values.keys())
    for r in range(1, 3):
        for combo in itertools.combinations(perms, r):
            perm_name = "_".join([c.lower() for c in combo])
            perm_flags = " | ".join(combo)
            body = f"syscall(SYS_keyctl, KEYCTL_SETPERM, -1, {perm_flags});"
            content = f"{common_headers}\n{key_perm_defines}\n\nint main() {{\n    {body}\n    return 0;\n}}\n"
            write_c_file(f"keyctl_setperm_{perm_name}", content)

def main():
    cmds = {
        "GET_KEYRING_ID": "syscall(SYS_keyctl, KEYCTL_GET_KEYRING_ID, -1, 1);",
        "JOIN_SESSION_KEYRING": 'syscall(SYS_keyctl, KEYCTL_JOIN_SESSION_KEYRING, \"session\");',
        "UPDATE": 'char payload[] = \"data\";\nsyscall(SYS_keyctl, KEYCTL_UPDATE, -1, payload, sizeof(payload));',
        "REVOKE": "syscall(SYS_keyctl, KEYCTL_REVOKE, -1);",
        "DESCRIBE": "char desc[64];\nsyscall(SYS_keyctl, KEYCTL_DESCRIBE, -1, desc, sizeof(desc));",
        "CLEAR": "syscall(SYS_keyctl, KEYCTL_CLEAR, -1);",
        "LINK": "syscall(SYS_keyctl, KEYCTL_LINK, -1, -1);",
        "UNLINK": "syscall(SYS_keyctl, KEYCTL_UNLINK, -1, -1);",
        "SEARCH": 'syscall(SYS_keyctl, KEYCTL_SEARCH, -1, \"user\", \"desc\", -1);',
        "READ": "char buf[64];\nsyscall(SYS_keyctl, KEYCTL_READ, -1, buf, sizeof(buf));",
        "CHOWN": "syscall(SYS_keyctl, KEYCTL_CHOWN, -1, 1000, 1000);",
        "INSTANTIATE": 'char payload[] = \"payload\";\nsyscall(SYS_keyctl, KEYCTL_INSTANTIATE, -1, payload, sizeof(payload), -1);',
        "NEGATE": "syscall(SYS_keyctl, KEYCTL_NEGATE, -1, 10, -1);",
        "SET_TIMEOUT": "syscall(SYS_keyctl, KEYCTL_SET_TIMEOUT, -1, 1000);",
        "ASSUME_AUTHORITY": "syscall(SYS_keyctl, KEYCTL_ASSUME_AUTHORITY, -1);",
        "GET_SECURITY": "char label[64];\nsyscall(SYS_keyctl, KEYCTL_GET_SECURITY, -1, label, sizeof(label));",
        "SESSION_TO_PARENT": "syscall(SYS_keyctl, KEYCTL_SESSION_TO_PARENT);",
        "REJECT": "syscall(SYS_keyctl, KEYCTL_REJECT, -1, 10, -1, -1);",
        "INVALIDATE": "syscall(SYS_keyctl, KEYCTL_INVALIDATE, -1);",
        "CAPABILITIES": "char buf[64];\nsyscall(SYS_keyctl, KEYCTL_CAPABILITIES, buf, sizeof(buf));",
        "WATCH_KEY": "syscall(SYS_keyctl, KEYCTL_WATCH_KEY, -1, -1, 0x01);"
    }

    for cmd, body in cmds.items():
        generate_basic_test(cmd, body)

    generate_setperm_tests()

if __name__ == "__main__":
    main()
