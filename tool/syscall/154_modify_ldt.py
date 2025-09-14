import os

def generate_modify_ldt_tests():
    output_dir = "./tool/cfiles/154_modify_ldt"
    os.makedirs(output_dir, exist_ok=True)

    user_desc_bases = [4096, 1048576, 536870912, 536872960, 536875008, -1]
    user_desc_limits = [0, 1024, 4096, 8192, 16384, -1]

    c_code = f"""#include <unistd.h>
#include <sys/syscall.h>

int main() {{
    char buffer[8192];
    if (syscall(SYS_modify_ldt, 0, buffer, sizeof(buffer)) == -1) return 1;
    return 0;
}}
"""
    filename = f"{output_dir}/modify_ldt_read.c"
    with open(filename, "w") as f:
        f.write(c_code)

    c_code = f"""#include <unistd.h>
#include <sys/syscall.h>

int main() {{
    char buffer[8192];
    if (syscall(SYS_modify_ldt, 2, buffer, sizeof(buffer)) == -1) return 1;
    return 0;
}}
"""
    filename = f"{output_dir}/modify_ldt_read_default.c"
    with open(filename, "w") as f:
        f.write(c_code)

    for base_addr in user_desc_bases:
        for limit in user_desc_limits:
            syscall_name = f"modify_ldt_write_base_{base_addr}_limit_{limit}"
            c_code = f"""#include <unistd.h>
#include <sys/syscall.h>
#include <string.h>

struct user_desc {{
    int entry_number;
    int base_addr;
    int limit;
    int seg_32bit : 1;
    int contents : 2;
    int read_exec_only : 1;
    int limit_in_pages : 1;
    int seg_not_present : 1;
    int useable : 1;
    int lm : 1;
}};

int main() {{
    struct user_desc desc;
    memset(&desc, 0, sizeof(desc));
    
    desc.entry_number = 0;
    desc.base_addr = {base_addr};
    desc.limit = {limit};
    desc.seg_32bit = 1;
    desc.contents = 0;
    desc.read_exec_only = 0;
    desc.limit_in_pages = 0;
    desc.seg_not_present = 0;
    desc.useable = 1;
    desc.lm = 0;

    if (syscall(SYS_modify_ldt, 1, &desc, sizeof(desc)) == -1) return 1;
    if (syscall(SYS_modify_ldt, 17, &desc, sizeof(desc)) == -1) return 1;

    return 0;
}}
"""
            filename = f"{output_dir}/{syscall_name}.c"
            with open(filename, "w") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_modify_ldt_tests()
