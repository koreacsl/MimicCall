import os
import textwrap

OUTPUT_DIR =  "./tool/cfiles/446_landlock_restrict_self"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FS_ACCESS_FLAGS = {
    "EXECUTE": 1 << 0, "WRITE_FILE": 1 << 1, "READ_FILE": 1 << 2,
    "READ_DIR": 1 << 3, "REMOVE_DIR": 1 << 4, "REMOVE_FILE": 1 << 5,
    "MAKE_CHAR": 1 << 6, "MAKE_DIR": 1 << 7, "MAKE_REG": 1 << 8,
    "MAKE_SOCK": 1 << 9, "MAKE_FIFO": 1 << 10, "MAKE_BLOCK": 1 << 11,
    "MAKE_SYM": 1 << 12, "REFER": 1 << 13, "TRUNCATE": 1 << 14,
}
ALL_FS_ACCESS_MASK = sum(FS_ACCESS_FLAGS.values())

C_TEMPLATE = textwrap.dedent("""\
    #define _GNU_SOURCE
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <unistd.h>
    #include <fcntl.h>
    #include <errno.h>
    #include <sys/prctl.h>
    #include <sys/syscall.h>
    #include <sys/stat.h>
    #include <stdint.h>

    #ifndef __NR_landlock_create_ruleset
    #define __NR_landlock_create_ruleset 444
    #endif
    #ifndef __NR_landlock_add_rule
    #define __NR_landlock_add_rule 445
    #endif
    #ifndef __NR_landlock_restrict_self
    #define __NR_landlock_restrict_self 446
    #endif

    #define LANDLOCK_RULE_PATH_BENEATH 1
    #ifndef LANDLOCK_CREATE_RULESET_VERSION
    #define LANDLOCK_CREATE_RULESET_VERSION (1U << 0)
    #endif

    struct landlock_ruleset_attr_v1 {{ uint64_t handled_access_fs; }};
    struct landlock_ruleset_attr_v4 {{ uint64_t handled_access_fs; uint64_t handled_access_net; }};
    struct landlock_path_beneath_attr {{ uint64_t allowed_access; int32_t parent_fd; }};

    static int get_landlock_abi(void) {{
        long r = syscall(__NR_landlock_create_ruleset, NULL, 0, LANDLOCK_CREATE_RULESET_VERSION);
        if (r < 0) return 1;
        return (int)r;
    }}

    static uint64_t fs_mask_for_abi(int abi) {{
        uint64_t v1 = 0;
        for (int b = 0; b <= 12; ++b) v1 |= (1ULL << b);
        uint64_t v2 = v1 | (1ULL << 13);
        uint64_t v3 = v2 | (1ULL << 14);
        if (abi >= 3) return v3;
        if (abi == 2) return v2;
        return v1;
    }}

    char test_dir_template[] = "/tmp/landlock_test_XXXXXX";
    char *test_dir = NULL;
    char test_file[512], test_subdir[512], other_file[512];

    void setup(void) {{
        test_dir = mkdtemp(test_dir_template);
        if (!test_dir) {{ perror("mkdtemp"); exit(1); }}
        close(open(test_file, O_WRONLY | O_CREAT, 0644));
        close(open(other_file, O_WRONLY | O_CREAT, 0644));
    }}

    void cleanup(void) {{
        unlink(test_file);
        rmdir(test_subdir);
        rmdir(test_dir);
        unlink(other_file);
    }}

    void attempt(const char* action, int success, int should_succeed) {{
        errno = 0;
    }}

    int main(int argc, char const *argv[]) {{
        setup();

        int abi = get_landlock_abi();

        uint64_t requested_handled = {handled_fs_mask};
        uint64_t requested_allowed = {allowed_fs_mask};
        uint64_t supported_fs = fs_mask_for_abi(abi);

        uint64_t handled_fs = requested_handled & supported_fs;
        uint64_t allowed_fs = requested_allowed & supported_fs;

        int ruleset_fd = -1;

        if (abi >= 4) {{
            const struct landlock_ruleset_attr_v4 attr4 = {{
                .handled_access_fs = handled_fs,
                .handled_access_net = 0,
            }};
            ruleset_fd = syscall(__NR_landlock_create_ruleset, &attr4, sizeof(attr4), 0);
            if (ruleset_fd < 0 && errno == E2BIG) abi = 1;
        }}
        if (ruleset_fd < 0 && abi < 4) {{
            const struct landlock_ruleset_attr_v1 attr1 = {{
                .handled_access_fs = handled_fs,
            }};
            ruleset_fd = syscall(__NR_landlock_create_ruleset, &attr1, sizeof(attr1), 0);
        }}
        if (ruleset_fd < 0) {{
            if (errno == ENOSYS) {{ cleanup(); return 77; }}
            perror("create_ruleset"); cleanup(); return 1;
        }}

        int dir_fd = open(test_dir, O_PATH | O_CLOEXEC);
        if (dir_fd < 0) {{ perror("open"); close(ruleset_fd); cleanup(); return 1; }}

        struct landlock_path_beneath_attr path_attr = {{
            .allowed_access = allowed_fs,
            .parent_fd = dir_fd
        }};

        if (syscall(__NR_landlock_add_rule, ruleset_fd, LANDLOCK_RULE_PATH_BENEATH, &path_attr, 0)) {{
            perror("add_rule"); close(dir_fd); close(ruleset_fd); cleanup(); return 1;
        }}
        close(dir_fd);

        if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)) {{ perror("prctl"); close(ruleset_fd); cleanup(); return 1; }}
        if (syscall(__NR_landlock_restrict_self, ruleset_fd, 0)) {{ perror("restrict_self"); close(ruleset_fd); cleanup(); return 1; }}
        close(ruleset_fd);

        const uint64_t allowed = {allowed_fs_mask};
        const uint64_t fs_read_file = {fs_read_file_flag};
        const uint64_t fs_write_file = {fs_write_file_flag};
        const uint64_t fs_make_dir = {fs_make_dir_flag};
        const uint64_t fs_remove_file = {fs_remove_file_flag};

        attempt("Read test file", open(test_file, O_RDONLY), allowed & fs_read_file);
        attempt("Write to test file", open(test_file, O_WRONLY | O_APPEND), allowed & fs_write_file);
        attempt("Make subdirectory", mkdir(test_subdir, 0755), allowed & fs_make_dir);
        attempt("Read file outside sandbox", open(other_file, O_RDONLY), 0);
        attempt("Write to file outside sandbox", open(other_file, O_WRONLY), 0);

        close(open(test_file, O_WRONLY | O_CREAT | O_TRUNC, 0644));
        attempt("Remove test file", unlink(test_file), allowed & fs_remove_file);

        cleanup();
        return 0;
    }}
""")

def write_c_file(name, content):
    filepath = os.path.join(OUTPUT_DIR, f"{name}.c")
    with open(filepath, "w") as f:
        f.write(content)

def generate_scenario(test_name, allowed_mask):
    content = C_TEMPLATE.format(
        handled_fs_mask=ALL_FS_ACCESS_MASK,
        allowed_fs_mask=allowed_mask,
        fs_read_file_flag=FS_ACCESS_FLAGS["READ_FILE"],
        fs_write_file_flag=FS_ACCESS_FLAGS["WRITE_FILE"],
        fs_make_dir_flag=FS_ACCESS_FLAGS["MAKE_DIR"],
        fs_remove_file_flag=FS_ACCESS_FLAGS["REMOVE_FILE"],
    )
    write_c_file(test_name, content)

def generate_all():
    readonly_mask = FS_ACCESS_FLAGS["READ_FILE"] | FS_ACCESS_FLAGS["READ_DIR"]
    generate_scenario("test_readonly_access", readonly_mask)

    writeonly_mask = FS_ACCESS_FLAGS["WRITE_FILE"] | FS_ACCESS_FLAGS["MAKE_REG"]
    generate_scenario("test_writeonly_access", writeonly_mask)

    manage_mask = (
        FS_ACCESS_FLAGS["MAKE_DIR"] | FS_ACCESS_FLAGS["MAKE_REG"] |
        FS_ACCESS_FLAGS["REMOVE_DIR"] | FS_ACCESS_FLAGS["REMOVE_FILE"]
    )
    generate_scenario("test_manage_access", manage_mask)

    full_mask = ALL_FS_ACCESS_MASK
    generate_scenario("test_full_access", full_mask)

    no_mask = 0
    generate_scenario("test_no_access", no_mask)

if __name__ == "__main__":
    generate_all()
