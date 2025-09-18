
import os

def generate_finit_module_tests():
    output_dir = "./tool/cfiles/313_finit_module"
    os.makedirs(output_dir, exist_ok=True)

    # NOTE: This test requires a pre-compiled kernel module at this path.
    # It must be run as root to succeed.
    module_path = "/tmp/test_module.ko"
    module_name = "test_module"

    finit_module_flags = {
        "MODULE_INIT_IGNORE_MODVERSIONS": 1,
        "MODULE_INIT_IGNORE_VERMAGIC": 2
    }
    delete_module_flags = {
        "O_NONBLOCK": 0x00004000,
        "O_TRUNC": 0x00000200
    }

    for finit_flag_name, finit_flag_value in finit_module_flags.items():
        for delete_flag_name, delete_flag_value in delete_module_flags.items():
            c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_finit_module
#define SYS_finit_module 313
#endif
#ifndef SYS_delete_module
#define SYS_delete_module 176
#endif

int main() {{
    const char *path = "{module_path}";
    int fd = -1;
    int result = -1;

    fd = open(path, O_RDONLY);
    if (fd == -1) return 1;

    if (syscall(SYS_finit_module, fd, "", {finit_flag_name}) != 0) {{
        close(fd);
        return 1;
    }}
    close(fd);

    result = syscall(SYS_delete_module, "{module_name}", {delete_flag_name});
    
    return (result == 0) ? 0 : 1;
}}
"""
            filename = os.path.join(output_dir, f"finit_module_{finit_flag_name.lower()}_{delete_flag_name.lower()}.c")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_finit_module_tests()
