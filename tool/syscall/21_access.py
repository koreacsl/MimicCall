import os

def generate_access_tests():
    output_dir = "./tool/cfiles/21_access"
    os.makedirs(output_dir, exist_ok=True)

    access_modes = {
        "F_OK": "f_ok",
        "R_OK": "r_ok",
        "W_OK": "w_ok",
        "X_OK": "x_ok"
    }

    for mode, name in access_modes.items():
        c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_access
#define SYS_access 21
#endif

int main() {{
    const char *path = "/dev/null";
    
    syscall(SYS_access, path, {mode});

    return 0;
}}
"""
        filename = f"{output_dir}/access_{name}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_access_tests()
