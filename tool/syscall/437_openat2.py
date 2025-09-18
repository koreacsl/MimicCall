
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
        # 경로: O_TMPFILE은 디렉터리를, 나머지는 파일(/dev/null)을 대상으로
        path = '"/tmp"' if flag == "O_TMPFILE" else '"/dev/null"'

        # 플래그 조합 규칙
        if flag == "O_PATH":
            final_flags = "O_PATH"                  # O_PATH는 단독 사용
            mode_expr   = "0"
        elif flag == "O_TMPFILE":
            final_flags = "O_TMPFILE | O_RDWR"      # O_TMPFILE은 R/W 동반 + mode 필요
            mode_expr   = "0600"
        else:
            final_flags = f"O_RDWR | {flag}"
            # O_CREAT 조합일 때만 mode 의미 있음(넣어도 무해)
            mode_expr   = "0644"

        c_code = f"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <string.h>
#include <stdint.h>

/* open_how 정의를 위해 linux/openat2.h 시도, 없으면 fallback */
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

/* 일부 환경에서 FASYNC 매크로가 없을 수 있음 → O_ASYNC로 매핑 */
#ifndef FASYNC
  #ifdef O_ASYNC
    #define FASYNC O_ASYNC
  #else
    #define FASYNC 0
  #endif
#endif

/* 일부 헤더에는 O_TMPFILE가 없을 수 있음 */
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
