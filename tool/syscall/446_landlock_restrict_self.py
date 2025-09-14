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
    struct landlock_ruleset_attr {{ __u64 handled_access_fs; __u64 handled_access_net; }};
    struct landlock_path_beneath_attr {{ __u64 allowed_access; __s32 parent_fd; }};

    char test_dir_template[] = "/tmp/landlock_test";
    char *test_dir = NULL;
    char test_file[512], test_subdir[512], other_file[512];

    void setup() {{
        test_dir = mkdtemp(test_dir_template);
        if (!test_dir) {{ perror("mkdtemp"); exit(1); }}
        snprintf(test_file, sizeof(test_file), "%s/test_file.txt", test_dir);
        snprintf(test_subdir, sizeof(test_subdir), "%s/subdir", test_dir);
        snprintf(other_file, sizeof(other_file), "/tmp/other_file.txt");
        close(open(test_file, O_WRONLY | O_CREAT, 0644));
        close(open(other_file, O_WRONLY | O_CREAT, 0644));
    }}

    void cleanup() {{
        unlink(test_file);
        rmdir(test_subdir);
        rmdir(test_dir);
        unlink(other_file);
    }}

    void attempt(const char* action, int success, int should_succeed) {{
        if ((success >= 0) == should_succeed) {{
            printf("[  OK  ] %s: %s as expected.\\n", action, should_succeed ? "Succeeded" : "Failed");
        }} else {{
            fprintf(stderr, "[ FAIL ] %s: %s unexpectedly (errno: %d %s).\\n",
                    action, should_succeed ? "Failed" : "Succeeded", errno, strerror(errno));
        }}
        errno = 0;
    }}

    int main(int argc, char const *argv[]) {{
        setup();

        const struct landlock_ruleset_attr attr = {{ .handled_access_fs = {handled_fs_mask}, .handled_access_net = 0 }};
        int ruleset_fd = syscall(__NR_landlock_create_ruleset, &attr, sizeof(attr), 0);
        if (ruleset_fd < 0) {{ if (errno == ENOSYS) {{ cleanup(); return 77;}} perror("create_ruleset"); cleanup(); return 1; }}

        int dir_fd = open(test_dir, O_PATH | O_CLOEXEC);
        if (dir_fd < 0) {{ perror("open"); close(ruleset_fd); cleanup(); return 1; }}
        
        struct landlock_path_beneath_attr path_attr = {{ .allowed_access = {allowed_fs_mask}, .parent_fd = dir_fd }};
        if (syscall(__NR_landlock_add_rule, ruleset_fd, LANDLOCK_RULE_PATH_BENEATH, &path_attr, 0)) {{
            perror("add_rule"); close(dir_fd); close(ruleset_fd); cleanup(); return 1;
        }}
        close(dir_fd);
        
        if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)) {{ perror("prctl"); close(ruleset_fd); cleanup(); return 1; }}
        if (syscall(__NR_landlock_restrict_self, ruleset_fd, 0)) {{ perror("restrict_self"); close(ruleset_fd); cleanup(); return 1; }}
        close(ruleset_fd);

        const __u64 allowed = {allowed_fs_mask};
        const __u64 fs_read_file = {fs_read_file_flag};
        const __u64 fs_write_file = {fs_write_file_flag};
        const __u64 fs_make_dir = {fs_make_dir_flag};
        const __u64 fs_remove_file = {fs_remove_file_flag};

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
        test_name=test_name,
        handled_fs_mask=ALL_FS_ACCESS_MASK,
        allowed_fs_mask=allowed_mask,
        fs_read_file_flag=FS_ACCESS_FLAGS["READ_FILE"],
        fs_write_file_flag=FS_ACCESS_FLAGS["WRITE_FILE"],
        fs_make_dir_flag=FS_ACCESS_FLAGS["MAKE_DIR"],
        fs_remove_file_flag=FS_ACCESS_FLAGS["REMOVE_FILE"]
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

