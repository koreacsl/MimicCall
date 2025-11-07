
import os

def generate_inotify_rm_watch_tests():
    output_dir = "./tool/cfiles/255_inotify_rm_watch"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>
#include <sys/inotify.h>

#ifndef SYS_inotify_init1
#define SYS_inotify_init1 294
#endif
#ifndef SYS_inotify_add_watch
#define SYS_inotify_add_watch 254
#endif
#ifndef SYS_inotify_rm_watch
#define SYS_inotify_rm_watch 255
#endif

int main() {
    int fd = syscall(SYS_inotify_init1, 0);
    if (fd < 0) return 1;

    int wd = syscall(SYS_inotify_add_watch, fd, "/tmp", IN_ACCESS);
    if (wd < 0) {
        close(fd);
        return 1;
    }

    if (syscall(SYS_inotify_rm_watch, fd, wd) == -1) {
        close(fd);
        return 1;
    }
    
    close(fd);
    return 0;
}
"""
    filename = os.path.join(output_dir, "inotify_rm_watch.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_inotify_rm_watch_tests()
