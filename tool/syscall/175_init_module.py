
import os

def generate_init_module_tests():
    output_dir = "./tool/cfiles/175_init_module"
    os.makedirs(output_dir, exist_ok=True)

    # NOTE: This test requires a pre-compiled kernel module at this path.
    # It must be run as root to succeed.
    module_path = "/tmp/test_module.ko"
    module_name = "test_module"
    
    delete_module_flags = {
        "O_NONBLOCK": 0x00004000,
        "O_TRUNC": 0x00000200
    }

    for flag_name, flag_value in delete_module_flags.items():
        c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <stdlib.h>

#ifndef SYS_init_module
#define SYS_init_module 175
#endif
#ifndef SYS_delete_module
#define SYS_delete_module 176
#endif

int main() {{
    const char *path = "{module_path}";
    void *module_image = NULL;
    int fd = -1;
    long module_size = 0;
    int result = -1;

    fd = open(path, O_RDONLY);
    if (fd == -1) return 1;

    module_size = lseek(fd, 0, SEEK_END);
    if (module_size <= 0) {{
        close(fd);
        return 1;
    }}
    lseek(fd, 0, SEEK_SET);

    module_image = malloc(module_size);
    if (!module_image) {{
        close(fd);
        return 1;
    }}

    if (read(fd, module_image, module_size) != module_size) {{
        free(module_image);
        close(fd);
        return 1;
    }}
    close(fd);

    if (syscall(SYS_init_module, module_image, module_size, "") != 0) {{
        free(module_image);
        return 1;
    }}
    free(module_image);

    result = syscall(SYS_delete_module, "{module_name}", {flag_name});
    
    return (result == 0) ? 0 : 1;
}}
"""
        filename = os.path.join(output_dir, f"init_module_{flag_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_init_module_tests()
