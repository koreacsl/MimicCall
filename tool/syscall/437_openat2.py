
import os

def generate_openat2_tests():
    output_dir = "./tool/cfiles/437_openat2"
    os.makedirs(output_dir, exist_ok=True)

    open_flags = [
        "O_WRONLY", "O_RDWR", "O_APPEND", "FASYNC", "O_CLOEXEC", "O_CREAT", "O_DIRECT",
        "O_DIRECTORY", "O_EXCL", "O_LARGEFILE", "O_NOATIME", "O_NOCTTY", "O_NOFOLLOW",
        "O_NONBLOCK", "O_PATH", "O_SYNC", "O_TRUNC", "O_TMPFILE"
    ]

    for flag in open_flags:
        path = '"/tmp"' if flag == "O_TMPFILE" else '"/dev/null"'

        if flag == "O_PATH":
            final_flags = "O_PATH"                 
            mode_expr   = "0"
        elif flag == "O_TMPFILE":
            final_flags = "O_TMPFILE | O_RDWR"      
            mode_expr   = "0600"
        else:
            final_flags = f"O_RDWR | {flag}"
            mode_expr   = "0644"

        c_code = f"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <string.h>
#include <stdint.h>

#if __has_include(<linux/openat2.h>)
  #include <linux/openat2.h>
#else
  struct open_how {{
      uint64_t flags;
      uint64_t mode;
      uint64_t resolve;
  }};
#endif

#ifndef SYS_openat2
#define SYS_openat2 437
#endif

#ifndef FASYNC
  #ifdef O_ASYNC
    #define FASYNC O_ASYNC
  #else
    #define FASYNC 0
  #endif
#endif

#ifndef O_TMPFILE
#define O_TMPFILE 020000000
#endif

int main(void) {{
    struct open_how how;
    memset(&how, 0, sizeof(how));
    how.flags = {final_flags};
    how.mode  = {mode_expr};

    int fd = syscall(SYS_openat2, AT_FDCWD, {path}, &how, sizeof(how));
    if (fd == -1) {{
        return 1;
    }}
    close(fd);
    return 0;
}}
"""
        filename = f"{output_dir}/openat2_{flag.lower()}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_openat2_tests()
