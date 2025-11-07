
import os

def generate_faccessat2_tests():
    output_dir = "./tool/cfiles/439_faccessat2"
    os.makedirs(output_dir, exist_ok=True)

    open_modes = {
        "read": "R_OK",
        "write": "W_OK",
        "exec": "X_OK"
    }
    
    faccessat_flags = {
        "none": "0",
        "eaccess": "AT_EACCESS",
        "symlink_nofollow": "AT_SYMLINK_NOFOLLOW"
    }

    for mode_name, mode_value in open_modes.items():
        for flag_name, flag_value in faccessat_flags.items():
            c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_faccessat2
#define SYS_faccessat2 439
#endif

#ifndef AT_EACCESS
#define AT_EACCESS 0x200
#endif
#ifndef AT_SYMLINK_NOFOLLOW
#define AT_SYMLINK_NOFOLLOW 0x100
#endif

int main() {{
    const char *path = "/tmp/test_faccessat2_file";
    
    int fd = open(path, O_CREAT | O_WRONLY, 0755);
    if (fd == -1) return 1;
    close(fd);

    syscall(SYS_faccessat2, AT_FDCWD, path, {mode_value}, {flag_value});

    unlink(path);
    return 0;
}}
"""
            filename = os.path.join(output_dir, f"faccessat2_{mode_name}_{flag_name}.c")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_faccessat2_tests()
