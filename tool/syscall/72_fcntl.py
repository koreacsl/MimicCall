import os

def generate_test(filename, includes, variables, main_code):
    c_code = f"""{includes}

#ifndef F_ADD_SEALS
#define F_ADD_SEALS 1033
#endif

#ifndef F_DUPFD
#define F_DUPFD 0
#endif

#ifndef F_DUPFD_CLOEXEC
#define F_DUPFD_CLOEXEC 1030
#endif

#ifndef F_GETFD
#define F_GETFD 1
#endif

#ifndef F_GETFL
#define F_GETFL 3
#endif

#ifndef F_GETLEASE
#define F_GETLEASE 1025
#endif

#ifndef F_GETLK
#define F_GETLK 5
#endif

#ifndef F_GETOWN
#define F_GETOWN 9
#endif

#ifndef F_GETOWN_EX
#define F_GETOWN_EX 16
#endif

#ifndef F_GETPIPE_SZ
#define F_GETPIPE_SZ 1032
#endif

#ifndef F_GETSIG
#define F_GETSIG 11
#endif

#ifndef F_GET_FILE_RW_HINT
#define F_GET_FILE_RW_HINT 1037
#endif

#ifndef F_GET_RW_HINT
#define F_GET_RW_HINT 1035
#endif

#ifndef F_GET_SEALS
#define F_GET_SEALS 1034
#endif

#ifndef F_NOTIFY
#define F_NOTIFY 1026
#endif

#ifndef F_OFD_GETLK
#define F_OFD_GETLK 36
#endif

#ifndef F_OFD_SETLK
#define F_OFD_SETLK 37
#endif

#ifndef F_OFD_SETLKW
#define F_OFD_SETLKW 38
#endif

#ifndef F_OWNER_PGRP
#define F_OWNER_PGRP 2
#endif

#ifndef F_OWNER_PID
#define F_OWNER_PID 1
#endif

#ifndef F_OWNER_TID
#define F_OWNER_TID 0
#endif

#ifndef F_RDLCK
#define F_RDLCK 0
#endif

#ifndef F_SEAL_GROW
#define F_SEAL_GROW 4
#endif

#ifndef F_SEAL_SEAL
#define F_SEAL_SEAL 1
#endif

#ifndef F_SEAL_SHRINK
#define F_SEAL_SHRINK 2
#endif

#ifndef F_SEAL_WRITE
#define F_SEAL_WRITE 8
#endif

#ifndef F_SETFD
#define F_SETFD 2
#endif

#ifndef F_SETFL
#define F_SETFL 4
#endif

#ifndef F_SETLEASE
#define F_SETLEASE 1024
#endif

#ifndef F_SETLK
#define F_SETLK 6
#endif

#ifndef F_SETLKW
#define F_SETLKW 7
#endif

#ifndef F_SETOWN
#define F_SETOWN 8
#endif

#ifndef F_SETOWN_EX
#define F_SETOWN_EX 15
#endif

#ifndef F_SETPIPE_SZ
#define F_SETPIPE_SZ 1031
#endif

#ifndef F_SETSIG
#define F_SETSIG 10
#endif

#ifndef F_SET_FILE_RW_HINT
#define F_SET_FILE_RW_HINT 1038
#endif

#ifndef F_SET_RW_HINT
#define F_SET_RW_HINT 1036
#endif

#ifndef F_UNLCK
#define F_UNLCK 2
#endif

#ifndef F_WRLCK
#define F_WRLCK 1
#endif

#ifndef DN_CREATE
#define DN_CREATE 4
#endif

#ifndef DN_DELETE
#define DN_DELETE 8
#endif

#ifndef DN_MODIFY
#define DN_MODIFY 2
#endif

#ifndef DN_MULTISHOT
#define DN_MULTISHOT 2147483648
#endif

#ifndef DN_RENAME
#define DN_RENAME 16
#endif

#ifndef DN_ATTRIB
#define DN_ATTRIB 32
#endif

#ifndef DN_ACCESS
#define DN_ACCESS 1
#endif

#ifndef O_DIRECT
#define O_DIRECT 16384
#endif

#ifndef O_NOATIME
#define O_NOATIME 262144
#endif

#ifndef RWH_WRITE_LIFE_LONG
#define RWH_WRITE_LIFE_LONG 4
#endif

#ifndef RWH_WRITE_LIFE_SHORT
#define RWH_WRITE_LIFE_SHORT 2
#endif

#ifndef HAVE_STRUCT_F_OWNER_EX
struct f_owner_ex {{
    int type;
    pid_t pid;
}};
#define HAVE_STRUCT_F_OWNER_EX
#endif

int main() {{
    int fd = open("./testfile", O_CREAT | O_RDWR, 0644);
    if (fd == -1) return 1;

    {variables}

    {main_code}
    
    close(fd);
    return result;
}}
"""
    with open(filename, "w") as f:
        f.write(c_code)

def generate_fcntl_tests():
    output_dir = "./tool/cfiles/72_fcntl"
    os.makedirs(output_dir, exist_ok=True)

    fcntl_lock_flags = ["F_SETLK", "F_SETLKW", "F_GETLK", "F_OFD_GETLK", "F_OFD_SETLK", "F_OFD_SETLKW"]
    flock_types = ["F_RDLCK", "F_WRLCK", "F_UNLCK"]
    seek_whence_flags = ["SEEK_SET", "SEEK_CUR", "SEEK_END", "SEEK_DATA", "SEEK_HOLE"]

    fcntl_owner_ex_flags = ["F_GETOWN_EX", "F_SETOWN_EX"]
    owner_types = ["F_OWNER_TID", "F_OWNER_PID", "F_OWNER_PGRP"]

    fcntl_no_arg = {
        "fcntl_dupfd": ["F_DUPFD", "F_DUPFD_CLOEXEC"],
        "fcntl_getflags": ["F_GETFD", "F_GETFL", "F_GETSIG", "F_GETLEASE", "F_GETPIPE_SZ", "F_GET_SEALS"],
        "fcntl_getown": ["F_GETOWN"]
    }
    
    fcntl_with_fixed_arg = {
        "fcntl_setown": ("F_SETOWN", "getpid()"),
        "fcntl_setpipe": ("F_SETPIPE_SZ", "4096")
    }
    
    fcntl_misc_flags = {
        "F_SETFD": ["FD_CLOEXEC"],
        "F_SETFL": ["O_APPEND", "FASYNC", "O_DIRECT", "O_NOATIME", "O_NONBLOCK"],
        "F_SETSIG": ["SIGIO"],
        "F_SETLEASE": ["F_RDLCK", "F_WRLCK", "F_UNLCK"],
        "F_NOTIFY": ["DN_MULTISHOT", "DN_ACCESS", "DN_MODIFY", "DN_CREATE", "DN_DELETE", "DN_RENAME", "DN_ATTRIB"],
        "F_ADD_SEALS": ["F_SEAL_SEAL", "F_SEAL_SHRINK", "F_SEAL_GROW", "F_SEAL_WRITE"]
    }
    
    fcntl_rw_hint_flags = ["F_GET_RW_HINT", "F_SET_RW_HINT", "F_GET_FILE_RW_HINT", "F_SET_FILE_RW_HINT"]
    rw_hint_values = ["RWH_WRITE_LIFE_SHORT", "RWH_WRITE_LIFE_LONG"]

    includes = """#include <fcntl.h>\n#include <unistd.h>\n#include <sys/types.h>\n#include <sys/file.h>\n#include <sys/stat.h>\n#include <stdint.h>\n#include <linux/fs.h>\n#include <sys/inotify.h>\n#include <sys/mman.h>\n#include <signal.h>"""
    
    for lock_flag in fcntl_lock_flags:
        for lock_type in flock_types:
            for seek_flag in seek_whence_flags:
                filename = f"{output_dir}/fcntl_{lock_flag.lower()}_{lock_type.lower()}_{seek_flag.lower()}.c"
                variables = f"struct flock lock = {{ .l_type = {lock_type}, .l_whence = {seek_flag}, .l_start = 0, .l_len = 0, .l_pid = getpid() }};"
                main_code = f"int result = fcntl(fd, {lock_flag}, &lock);"
                generate_test(filename, includes, variables, main_code)

    for cmd in fcntl_owner_ex_flags:
        for owner_type in owner_types:
            filename = f"{output_dir}/fcntl_{cmd.lower()}_{owner_type.lower()}.c"
            variables = f"struct f_owner_ex owner = {{ .type = {owner_type}, .pid = getpid() }};"
            main_code = f"int result = fcntl(fd, {cmd}, &owner);"
            generate_test(filename, includes, variables, main_code)

    for syscall_name, flags in fcntl_no_arg.items():
        for flag in flags:
            filename = f"{output_dir}/fcntl_{syscall_name}_{flag.lower()}.c"
            generate_test(filename, includes, "", f"int result = fcntl(fd, {flag});")

    for syscall_name, (cmd, arg) in fcntl_with_fixed_arg.items():
        filename = f"{output_dir}/fcntl_{syscall_name}_{cmd.lower()}.c"
        generate_test(filename, includes, "", f"int result = fcntl(fd, {cmd}, {arg});")

    for cmd, flags_list in fcntl_misc_flags.items():
        for flag in flags_list:
            filename = f"{output_dir}/fcntl_{cmd.lower()}_{flag.lower()}.c"
            generate_test(filename, includes, "", f"int result = fcntl(fd, {cmd}, {flag});")

    for cmd in fcntl_rw_hint_flags:
        for hint_value in rw_hint_values:
            filename = f"{output_dir}/fcntl_{cmd.lower()}_{hint_value.lower()}.c"
            variables = "int64_t hint = " + hint_value + ";"
            main_code = f"int result = fcntl(fd, {cmd}, &hint);"
            generate_test(filename, includes, variables, main_code)


if __name__ == "__main__":
    generate_fcntl_tests()
