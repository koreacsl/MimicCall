import os

def generate_renameat2_tests():
    output_dir = "./tool/cfiles/316_renameat2"
    os.makedirs(output_dir, exist_ok=True)

    renameat2_flags = {
        "RENAME_EXCHANGE": 2,
        "RENAME_NOREPLACE": 1,
        "RENAME_WHITEOUT": 4
    }

    for flag_name, flag_value in renameat2_flags.items():
        c_code = f"""#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_renameat2
#define SYS_renameat2 316
#endif

#ifndef {flag_name}
#define {flag_name} {flag_value}
#endif

int main() {{
    const char* old_path = "/tmp/testfile_renameat2_old";
    const char* new_path = "/tmp/testfile_renameat2_new";

    remove(old_path);
    remove(new_path);

    int fd_old = open(old_path, O_RDWR | O_CREAT, 0666);
    if (fd_old == -1) {{
        return 1;
    }}
    close(fd_old);

    if ({flag_value} == RENAME_EXCHANGE) {{
        int fd_new = open(new_path, O_RDWR | O_CREAT, 0666);
        if (fd_new == -1) {{
            remove(old_path);
            return 1;
        }}
        close(fd_new);
    }}

    if (syscall(SYS_renameat2, AT_FDCWD, old_path, AT_FDCWD, new_path, {flag_name}) == -1) {{
        remove(old_path);
        remove(new_path);
        return 1;
    }}

    remove(old_path);
    remove(new_path);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"renameat2_{flag_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_renameat2_tests()
