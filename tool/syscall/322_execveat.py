
import os

def generate_execveat_tests():
    output_dir = "./tool/cfiles/322_execveat"
    os.makedirs(output_dir, exist_ok=True)

    execveat_flags = [
        "0",
        "AT_EMPTY_PATH",
        "AT_SYMLINK_NOFOLLOW"
    ]

    for flag in execveat_flags:
        
        c_code = f"""#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <errno.h>

#ifndef SYS_execveat
#define SYS_execveat 322
#endif

int main() {{
    char *argv[] = {{"/bin/true", NULL}};
    char *envp[] = {{NULL}};
    int dirfd = AT_FDCWD;
    const char *pathname = "/bin/true";
    int flags = {flag};

    if (flags & AT_EMPTY_PATH) {{
        dirfd = open("/bin/true", O_PATH);
        if (dirfd == -1) {{
            return 1;
        }}
        pathname = "";
    }}

    syscall(SYS_execveat, dirfd, pathname, argv, envp, flags);
    
    if (flags & AT_EMPTY_PATH) {{
        close(dirfd);
    }}

    return 1;
}}
"""
        filename = os.path.join(output_dir, f"test_execveat_{flag.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_execveat_tests()
