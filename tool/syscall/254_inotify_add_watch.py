
import os

def generate_inotify_add_watch_tests():
    output_dir = "./tool/cfiles/254_inotify_add_watch"
    os.makedirs(output_dir, exist_ok=True)

    inotify_masks = [
        "IN_ACCESS", "IN_ATTRIB", "IN_CLOSE_WRITE", "IN_CLOSE_NOWRITE", "IN_CREATE",
        "IN_DELETE", "IN_DELETE_SELF", "IN_MODIFY", "IN_MOVE_SELF", "IN_MOVED_FROM",
        "IN_MOVED_TO", "IN_OPEN", "IN_DONT_FOLLOW", "IN_EXCL_UNLINK", "IN_MASK_ADD",
        "IN_ONESHOT", "IN_ONLYDIR", "IN_ISDIR"
    ]

    for mask_str in inotify_masks:
        c_code = f"""#include <unistd.h>
#include <sys/syscall.h>
#include <sys/inotify.h>

#ifndef SYS_inotify_init1
#define SYS_inotify_init1 294
#endif
#ifndef SYS_inotify_add_watch
#define SYS_inotify_add_watch 254
#endif

int main() {{
    int fd = syscall(SYS_inotify_init1, 0);
    if (fd < 0) return 1;

    syscall(SYS_inotify_add_watch, fd, "/tmp", {mask_str});
    
    close(fd);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"inotify_add_watch_{mask_str.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_inotify_add_watch_tests()
