
import os

def generate_fanotify_mark_tests():
    output_dir = "./tool/cfiles/301_fanotify_mark"
    os.makedirs(output_dir, exist_ok=True)

    mark_flags = {
        "add": "FAN_MARK_ADD",
        "remove": "FAN_MARK_REMOVE",
        "flush": "FAN_MARK_FLUSH",
        "dont_follow": "FAN_MARK_DONT_FOLLOW",
        "onlydir": "FAN_MARK_ONLYDIR",
        "mount": "FAN_MARK_MOUNT",
        "ignored_mask": "FAN_MARK_IGNORED_MASK",
        "ignored_surv_modify": "FAN_MARK_IGNORED_SURV_MODIFY",
        "evictable": "FAN_MARK_EVICTABLE"
    }

    mask_flags = {
        "access": "FAN_ACCESS",
        "modify": "FAN_MODIFY",
        "close_write": "FAN_CLOSE_WRITE",
        "close_nowrite": "FAN_CLOSE_NOWRITE",
        "open": "FAN_OPEN",
        "open_exec": "FAN_OPEN_EXEC",
        "ondir": "FAN_ONDIR",
        "event_on_child": "FAN_EVENT_ON_CHILD"
    }

    for mark_name, mark_value in mark_flags.items():
        if mark_name == "flush":
            # FAN_MARK_FLUSH does not use a mask.
            c_code = f"""#include <sys/fanotify.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <fcntl.h>
#include <sys/stat.h>

#ifndef SYS_fanotify_init
#define SYS_fanotify_init 300
#endif
#ifndef SYS_fanotify_mark
#define SYS_fanotify_mark 301
#endif

int main() {{
    const char *path = "/tmp/fanotify_test_dir";
    int fan_fd = -1;

    mkdir(path, 0755);
    fan_fd = syscall(SYS_fanotify_init, FAN_CLASS_NOTIF, O_RDONLY);
    if (fan_fd == -1) {{
        rmdir(path);
        return 1;
    }}
    
    syscall(SYS_fanotify_mark, fan_fd, {mark_value}, 0, 0, NULL);

    close(fan_fd);
    rmdir(path);
    return 0;
}}
"""
            filename = os.path.join(output_dir, f"test_{mark_name}.c")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(c_code)
        else:
            for mask_name, mask_value in mask_flags.items():
                c_code = f"""#include <sys/fanotify.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <fcntl.h>
#include <sys/stat.h>

#ifndef SYS_fanotify_init
#define SYS_fanotify_init 300
#endif
#ifndef SYS_fanotify_mark
#define SYS_fanotify_mark 301
#endif

int main() {{
    const char *path = "/tmp/fanotify_test_dir";
    int fan_fd = -1;

    mkdir(path, 0755);

    fan_fd = syscall(SYS_fanotify_init, FAN_CLASS_NOTIF, O_RDONLY);
    if (fan_fd == -1) {{
        rmdir(path);
        return 1;
    }}
    
    syscall(SYS_fanotify_mark, fan_fd, {mark_value}, {mask_value}, AT_FDCWD, path);

    close(fan_fd);
    rmdir(path);

    return 0;
}}
"""
                filename = os.path.join(output_dir, f"fanotify_mark_{mark_name}_{mask_name}.c")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(c_code)

if __name__ == "__main__":
    generate_fanotify_mark_tests()

