# -*- coding: utf-8 -*-
import os

def generate_fchownat_tests():
    output_dir = "./tool/cfiles/260_fchownat"
    os.makedirs(output_dir, exist_ok=True)

    flags = {
        "none": "0",
        "at_symlink_nofollow": "AT_SYMLINK_NOFOLLOW",
    }

    for name, flag in flags.items():
        if flag == "AT_SYMLINK_NOFOLLOW":
            setup_code = """
    const char* target_path = "/tmp/fchownat_test_target";
    const char* link_path = "/tmp/fchownat_test_link";
    
    unlink(target_path);
    unlink(link_path);

    int fd = open(target_path, O_CREAT, 0644);
    if (fd == -1) return 1;
    close(fd);

    if (symlink(target_path, link_path) == -1) {
        unlink(target_path);
        return 1;
    }
"""
            path_arg = "link_path"
            cleanup_code = """
    unlink(target_path);
    unlink(link_path);
"""
        else:
            setup_code = """
    const char* path = "/tmp/fchownat_test_file";
    unlink(path);
    int fd = open(path, O_CREAT, 0644);
    if (fd == -1) return 1;
    close(fd);
"""
            path_arg = "path"
            cleanup_code = "    unlink(path);"

        c_code = f"""#define _GNU_SOURCE
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>

#ifndef SYS_fchownat
#define SYS_fchownat 261
#endif

int main() {{
    uid_t uid = getuid();
    gid_t gid = getgid();

    {setup_code}

    if (syscall(SYS_fchownat, AT_FDCWD, {path_arg}, uid, gid, {flag}) == -1) {{
        {cleanup_code}
        return 1;
    }}
    
    {cleanup_code}
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"fchownat_{name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_fchownat_tests()
