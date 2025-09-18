
import os

def generate_mkdirat_tests():
    output_dir = "./tool/cfiles/258_mkdirat"
    os.makedirs(output_dir, exist_ok=True)

    mode_sets = {
        "S_IRWXU": ["S_IRWXU"],
        "S_IRUSR_S_IWUSR": ["S_IRUSR", "S_IWUSR"],
        "S_IRWXG": ["S_IRWXG"],
        "S_IRWXO": ["S_IRWXO"],
        "S_IRWXU_S_IRWXG_S_IRWXO": ["S_IRWXU", "S_IRWXG", "S_IRWXO"],
    }

    for mode_name, macros in mode_sets.items():
        mode_expr = " | ".join(macros)
        c_code = f"""#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_mkdirat
#define SYS_mkdirat 258
#endif

int main(void) {{
    const char* path = "test_mkdirat_dir";
    const char* tmp_path = "/tmp/test_mkdirat_dir";

    rmdir(tmp_path);

    int dir_fd = open("/tmp", O_RDONLY | O_DIRECTORY);
    if (dir_fd == -1) {{
        return 1;
    }}

    if (syscall(SYS_mkdirat, dir_fd, path, {mode_expr}) == -1) {{
        close(dir_fd);
        return 1;
    }}

    close(dir_fd);

    if (rmdir(tmp_path) == -1) {{
        return 1;
    }}

    return 0;
}}
"""
        filename = os.path.join(output_dir, f"mkdirat_{mode_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_mkdirat_tests()
