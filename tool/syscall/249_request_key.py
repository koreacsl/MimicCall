# -*- coding: utf-8 -*-
import os

def generate_request_key_tests():
    output_dir = "./tool/cfiles/249_request_key"
    os.makedirs(output_dir, exist_ok=True)

    key_types = [
        "user", "keyring"
    ]

    for key_type_str in key_types:
        c_code = f"""#include <sys/syscall.h>
#include <keyutils.h>
#include <unistd.h>

#ifndef SYS_add_key
#define SYS_add_key 248
#endif
#ifndef SYS_request_key
#define SYS_request_key 249
#endif
#ifndef SYS_keyctl
#define SYS_keyctl 250
#endif

int main() {{
    const char *key_type = "{key_type_str}";
    const char *description = "test_req_key_desc";
    key_serial_t keyring_id, key_id, requested_key_id;

    keyring_id = add_key("keyring", "test_req_keyring", NULL, 0, KEY_SPEC_SESSION_KEYRING);
    if (keyring_id == -1) {{
        return 1;
    }}

    key_id = add_key(key_type, description, "payload", 7, keyring_id);
    if (key_id == -1) {{
        syscall(SYS_keyctl, KEYCTL_UNLINK, keyring_id, KEY_SPEC_SESSION_KEYRING);
        return 1;
    }}

    requested_key_id = syscall(SYS_request_key, key_type, description, NULL, keyring_id);

    if (requested_key_id != -1) {{
        syscall(SYS_keyctl, KEYCTL_REVOKE, requested_key_id);
    }}
    
    syscall(SYS_keyctl, KEYCTL_REVOKE, key_id);
    syscall(SYS_keyctl, KEYCTL_UNLINK, keyring_id, KEY_SPEC_SESSION_KEYRING);

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"request_key_{key_type_str}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_request_key_tests()
