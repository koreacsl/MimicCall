
import os

def generate_add_key_tests():
    output_dir = "./tool/cfiles/248_add_key"
    os.makedirs(output_dir, exist_ok=True)

    key_types = [
        "user", "keyring", "logon", "big_key"
    ]

    for key_type_str in key_types:
        c_code = f"""#include <sys/syscall.h>
#include <keyutils.h>
#include <unistd.h>
#include <errno.h>

#ifndef SYS_add_key
#define SYS_add_key 248
#endif
#ifndef SYS_keyctl
#define SYS_keyctl 250
#endif

int main() {{
    const char *key_type = "{key_type_str}";
    const char *description = "test_key_desc";
    const char *payload = "test_payload";
    key_serial_t keyring_id, key_id;

    keyring_id = add_key("keyring", "test_keyring", NULL, 0, KEY_SPEC_SESSION_KEYRING);
    if (keyring_id == -1) {{
        return 1;
    }}

    key_id = syscall(SYS_add_key, key_type, description, payload, sizeof(payload), keyring_id);
    
    if (key_id != -1) {{
        syscall(SYS_keyctl, KEYCTL_REVOKE, key_id);
    }}

    syscall(SYS_keyctl, KEYCTL_UNLINK, keyring_id, KEY_SPEC_SESSION_KEYRING);

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"add_key_{key_type_str}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_add_key_tests()
