# -*- coding: utf-8 -*-
import os

def generate_capget_tests():
    output_dir = "./tool/cfiles/125_capget"
    os.makedirs(output_dir, exist_ok=True)

    cap_versions = [
        "_LINUX_CAPABILITY_VERSION_1",
        "_LINUX_CAPABILITY_VERSION_2",
        "_LINUX_CAPABILITY_VERSION_3"
    ]

    for version_name in cap_versions:
        c_code = f"""#include <unistd.h>
#include <sys/syscall.h>
#include <string.h>

#ifndef SYS_capget
#define SYS_capget 125
#endif

#ifndef _LINUX_CAPABILITY_VERSION_1
#define _LINUX_CAPABILITY_VERSION_1 0x19980330
#endif
#ifndef _LINUX_CAPABILITY_VERSION_2
#define _LINUX_CAPABILITY_VERSION_2 0x20071026
#endif
#ifndef _LINUX_CAPABILITY_VERSION_3
#define _LINUX_CAPABILITY_VERSION_3 0x20080522
#endif

struct __user_cap_header_struct {{
    unsigned int version;
    int pid;
}};

struct __user_cap_data_struct {{
    unsigned int effective;
    unsigned int permitted;
    unsigned int inheritable;
}};

int main() {{
    struct __user_cap_header_struct hdr;
    struct __user_cap_data_struct data[2];

    memset(&hdr, 0, sizeof(hdr));
    memset(&data, 0, sizeof(data));

    hdr.version = {version_name};
    hdr.pid = 0;

    if (syscall(SYS_capget, &hdr, data) == -1) {{
        return 1;
    }}

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"capget_{version_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_capget_tests()