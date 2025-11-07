
import os
import itertools
import textwrap

OUTPUT_DIR = "./tool/cfiles/444_landlock_create_ruleset"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FS_ACCESS_FLAGS = {
    "EXECUTE": 1 << 0, "WRITE_FILE": 1 << 1, "READ_FILE": 1 << 2,
    "READ_DIR": 1 << 3, "REMOVE_DIR": 1 << 4, "REMOVE_FILE": 1 << 5,
    "MAKE_CHAR": 1 << 6, "MAKE_DIR": 1 << 7, "MAKE_REG": 1 << 8,
    "MAKE_SOCK": 1 << 9, "MAKE_FIFO": 1 << 10, "MAKE_BLOCK": 1 << 11,
    "MAKE_SYM": 1 << 12, "REFER": 1 << 13, "TRUNCATE": 1 << 14,
}
NET_ACCESS_FLAGS = {"BIND_TCP": 1 << 0, "CONNECT_TCP": 1 << 1}

ALL_FS_ACCESS_MASK = sum(FS_ACCESS_FLAGS.values())
ALL_NET_ACCESS_MASK = sum(NET_ACCESS_FLAGS.values())

C_TEMPLATE = textwrap.dedent(r"""\
    #define _GNU_SOURCE
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <errno.h>
    #include <sys/syscall.h>
    #include <stdint.h>

    #ifndef __NR_landlock_create_ruleset
    #define __NR_landlock_create_ruleset 444
    #endif

    struct landlock_ruleset_attr {{
        uint64_t handled_access_fs;
        uint64_t handled_access_net;
    }};

    int main(int argc, char const *argv[]) {{
        const struct landlock_ruleset_attr attr = {{
            .handled_access_fs  = (uint64_t){handled_fs_mask},
            .handled_access_net = (uint64_t){handled_net_mask},
        }};

        int ruleset_fd = syscall(__NR_landlock_create_ruleset, &attr, sizeof(attr), 0);

        if (ruleset_fd >= 0) {{
            close(ruleset_fd);
            return EXIT_SUCCESS;
        }} else {{
            if (errno == ENOSYS) {{
                return 77;
            }}
            if (errno == EINVAL) {{
                return EXIT_SUCCESS;
            }}
            return EXIT_FAILURE;
        }}
    }}
""")

def write_c_file(name, content):
    filepath = os.path.join(OUTPUT_DIR, f"{name}.c")
    with open(filepath, "w") as f:
        f.write(content)

def generate_all():
    for name, mask in FS_ACCESS_FLAGS.items():
        test_name = f"create_ruleset_fs_{name.lower()}"
        content = C_TEMPLATE.format(
            test_name=test_name,
            handled_fs_mask=mask,
            handled_net_mask=0
        )
        write_c_file(test_name, content)

    for name, mask in NET_ACCESS_FLAGS.items():
        test_name = f"create_ruleset_net_{name.lower()}"
        content = C_TEMPLATE.format(
            test_name=test_name,
            handled_fs_mask=0,
            handled_net_mask=mask
        )
        write_c_file(test_name, content)

    test_name_all_fs = "create_ruleset_fs_all"
    content_all_fs = C_TEMPLATE.format(
        test_name=test_name_all_fs,
        handled_fs_mask=ALL_FS_ACCESS_MASK,
        handled_net_mask=0
    )
    write_c_file(test_name_all_fs, content_all_fs)

    test_name_all_net = "create_ruleset_net_all"
    content_all_net = C_TEMPLATE.format(
        test_name=test_name_all_net,
        handled_fs_mask=0,
        handled_net_mask=ALL_NET_ACCESS_MASK
    )
    write_c_file(test_name_all_net, content_all_net)

    test_name_all = "create_ruleset_all"
    content_all = C_TEMPLATE.format(
        test_name=test_name_all,
        handled_fs_mask=ALL_FS_ACCESS_MASK,
        handled_net_mask=ALL_NET_ACCESS_MASK
    )
    write_c_file(test_name_all, content_all)

    test_name_empty = "create_ruleset_empty"
    content_empty = C_TEMPLATE.format(
        test_name=test_name_empty,
        handled_fs_mask=0,
        handled_net_mask=0
    )
    write_c_file(test_name_empty, content_empty)

if __name__ == "__main__":
    generate_all()
