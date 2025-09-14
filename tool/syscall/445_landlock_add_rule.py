import os
import textwrap

OUTPUT_DIR = "./tool/cfiles/445_landlock_add_rule"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FS_ACCESS_FLAGS = {
    "EXECUTE": 1 << 0, "WRITE_FILE": 1 << 1, "READ_FILE": 1 << 2,
    "READ_DIR": 1 << 3, "REMOVE_DIR": 1 << 4, "REMOVE_FILE": 1 << 5,
    "MAKE_CHAR": 1 << 6, "MAKE_DIR": 1 << 7, "MAKE_REG": 1 << 8,
    "MAKE_SOCK": 1 << 9, "MAKE_FIFO": 1 << 10, "MAKE_BLOCK": 1 << 11,
    "MAKE_SYM": 1 << 12, "REFER": 1 << 13, "TRUNCATE": 1 << 14,
}
NET_ACCESS_FLAGS = { "BIND_TCP": 1 << 0, "CONNECT_TCP": 1 << 1 }

C_TEMPLATE = textwrap.dedent("""\
    #define _GNU_SOURCE
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <unistd.h>
    #include <fcntl.h>
    #include <errno.h>
    #include <sys/syscall.h>
    #include <netinet/in.h>

    #ifndef __NR_landlock_create_ruleset
    #define __NR_landlock_create_ruleset 444
    #endif
    #ifndef __NR_landlock_add_rule
    #define __NR_landlock_add_rule 445
    #endif

    #define LANDLOCK_RULE_PATH_BENEATH 1
    #define LANDLOCK_RULE_NET_PORT 2

    struct landlock_ruleset_attr {{ __u64 handled_access_fs; __u64 handled_access_net; }};
    struct landlock_path_beneath_attr {{ __u64 allowed_access; __s32 parent_fd; }};
    struct landlock_net_port_attr {{ __u64 allowed_access; __s16 port; }};

    int main(int argc, char const *argv[]) {{
        const struct landlock_ruleset_attr attr = {{
            .handled_access_fs = {handled_fs_mask},
            .handled_access_net = {handled_net_mask},
        }};

        int ruleset_fd = syscall(__NR_landlock_create_ruleset, &attr, sizeof(attr), 0);
        if (ruleset_fd < 0) {{
            if (errno == ENOSYS) {{ return 77; }}
            perror("landlock_create_ruleset"); return EXIT_FAILURE;
        }}
        
        int ret = 0;

        {rule_addition_code}

        close(ruleset_fd);
        return ret == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
    }}
""")

PATH_BENEATH_CODE = textwrap.dedent("""\
        char template[] = "/tmp/landlock_test_XXXXXX";
        char* test_dir = mkdtemp(template);
        if (!test_dir) {{ perror("mkdtemp"); close(ruleset_fd); return EXIT_FAILURE; }}

        int dir_fd = open(test_dir, O_PATH | O_CLOEXEC);
        if (dir_fd < 0) {{ perror("open"); rmdir(test_dir); close(ruleset_fd); return EXIT_FAILURE; }}

        struct landlock_path_beneath_attr path_attr = {{
            .allowed_access = {allowed_mask},
            .parent_fd = dir_fd,
        }};
        ret = syscall(__NR_landlock_add_rule, ruleset_fd, LANDLOCK_RULE_PATH_BENEATH, &path_attr, 0);
        close(dir_fd);
        rmdir(test_dir);
""")

NET_PORT_CODE = textwrap.dedent("""\
        struct landlock_net_port_attr net_attr = {{
            .allowed_access = {allowed_mask},
            .port = htons(8080),
        }};
        ret = syscall(__NR_landlock_add_rule, ruleset_fd, LANDLOCK_RULE_NET_PORT, &net_attr, 0);
""")

def write_c_file(name, content):
    filepath = os.path.join(OUTPUT_DIR, f"{name}.c")
    with open(filepath, "w") as f:
        f.write(content)

def generate_all():
    test_name_path_ok = "add_rule_path_beneath_ok"
    rule_code_path_ok = PATH_BENEATH_CODE.format(allowed_mask=FS_ACCESS_FLAGS["READ_FILE"])
    content_path_ok = C_TEMPLATE.format(
        handled_fs_mask=FS_ACCESS_FLAGS["READ_FILE"],
        handled_net_mask=0,
        rule_addition_code=rule_code_path_ok
    )
    write_c_file(test_name_path_ok, content_path_ok)

    test_name_path_fail = "add_rule_path_beneath_fail_eperm"
    rule_code_path_fail = PATH_BENEATH_CODE.format(allowed_mask=FS_ACCESS_FLAGS["WRITE_FILE"])
    content_path_fail = C_TEMPLATE.format(
        handled_fs_mask=FS_ACCESS_FLAGS["READ_FILE"],
        handled_net_mask=0,
        rule_addition_code=rule_code_path_fail
    )
    write_c_file(test_name_path_fail, content_path_fail)
    
    test_name_net_ok = "add_rule_net_port_ok"
    rule_code_net_ok = NET_PORT_CODE.format(allowed_mask=NET_ACCESS_FLAGS["BIND_TCP"])
    content_net_ok = C_TEMPLATE.format(
        handled_fs_mask=0,
        handled_net_mask=NET_ACCESS_FLAGS["BIND_TCP"],
        rule_addition_code=rule_code_net_ok
    )
    write_c_file(test_name_net_ok, content_net_ok)

    test_name_net_fail = "add_rule_net_port_fail_eperm"
    rule_code_net_fail = NET_PORT_CODE.format(allowed_mask=NET_ACCESS_FLAGS["CONNECT_TCP"])
    content_net_fail = C_TEMPLATE.format(
        handled_fs_mask=0,
        handled_net_mask=NET_ACCESS_FLAGS["BIND_TCP"],
        rule_addition_code=rule_code_net_fail
    )
    write_c_file(test_name_net_fail, content_net_fail)

if __name__ == "__main__":
    generate_all()