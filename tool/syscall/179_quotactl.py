import os

output_dir = "./tool/cfiles/179_quotactl"
os.makedirs(output_dir, exist_ok=True)

commands = {
    "Q_SYNC": ["Q_SYNC_USR", "Q_SYNC_GRP", "Q_SYNC_PRJ"],
    "Q_QUOTAON": ["Q_QUOTAON_USR", "Q_QUOTAON_GRP", "Q_QUOTAON_PRJ"],
    "Q_QUOTAOFF": ["Q_QUOTAOFF_USR", "Q_QUOTAOFF_GRP", "Q_QUOTAOFF_PRJ"],
    "Q_GETFMT": ["Q_GETFMT_USR", "Q_GETFMT_GRP", "Q_GETFMT_PRJ"],
    "Q_GETINFO": ["Q_GETINFO_USR", "Q_GETINFO_GRP", "Q_GETINFO_PRJ"],
    "Q_SETINFO": ["Q_SETINFO_USR", "Q_SETINFO_GRP", "Q_SETINFO_PRJ"],
    "Q_GETQUOTA": ["Q_GETQUOTA_USR", "Q_GETQUOTA_GRP", "Q_GETQUOTA_PRJ"],
    "Q_SETQUOTA": ["Q_SETQUOTA_USR", "Q_SETQUOTA_GRP", "Q_SETQUOTA_PRJ"],
    "Q_GETNEXTQUOTA": ["Q_GETNEXTQUOTA_USR", "Q_GETNEXTQUOTA_GRP", "Q_GETNEXTQUOTA_PRJ"]
}

header = '''#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <sys/quota.h>
#include <sys/types.h>
#include <stdint.h>

#define Q_SYNC_USR 0x800001
#define Q_SYNC_GRP 0x800002
#define Q_SYNC_PRJ 0x800004
#define Q_QUOTAON_USR 0x100001
#define Q_QUOTAON_GRP 0x100002
#define Q_QUOTAON_PRJ 0x100004
#define Q_QUOTAOFF_USR 0x200001
#define Q_QUOTAOFF_GRP 0x200002
#define Q_QUOTAOFF_PRJ 0x200004
#define Q_GETFMT_USR 0x300001
#define Q_GETFMT_GRP 0x300002
#define Q_GETFMT_PRJ 0x300004
#define Q_GETINFO_USR 0x400001
#define Q_GETINFO_GRP 0x400002
#define Q_GETINFO_PRJ 0x400004
#define Q_SETINFO_USR 0x500001
#define Q_SETINFO_GRP 0x500002
#define Q_SETINFO_PRJ 0x500004
#define Q_GETQUOTA_USR 0x600001
#define Q_GETQUOTA_GRP 0x600002
#define Q_GETQUOTA_PRJ 0x600004
#define Q_SETQUOTA_USR 0x700001
#define Q_SETQUOTA_GRP 0x700002
#define Q_SETQUOTA_PRJ 0x700004
#define Q_GETNEXTQUOTA_USR 0x800001
#define Q_GETNEXTQUOTA_GRP 0x800002
#define Q_GETNEXTQUOTA_PRJ 0x800004
'''

def generate_test_code(syscall_name, cmd_flag, is_fd=False):
    suffix = "_fd" if is_fd else ""
    base_name = f"{syscall_name.lower()}{suffix}_{cmd_flag.lower()}"
    filepath = os.path.join(output_dir, f"{base_name}.c")
    syscall_func = "quotactl"

    if is_fd:
        arg_str = {
            "Q_SYNC": f"0, {cmd_flag}, 0, 0",
            "Q_QUOTAON": f"0, {cmd_flag}, 1000, \"/dev/null\"",
            "Q_QUOTAOFF": f"0, {cmd_flag}, 1000, 0",
            "Q_GETFMT": f"0, {cmd_flag}, 1000, (int[1]){{0}}",
            "Q_GETINFO": f"0, {cmd_flag}, 1000, (struct if_dqinfo[1]){{0}}",
            "Q_SETINFO": f"0, {cmd_flag}, 1000, (struct if_dqinfo[1]){{0}}",
            "Q_GETQUOTA": f"0, {cmd_flag}, 1000, (struct if_dqblk[1]){{0}}",
            "Q_SETQUOTA": f"0, {cmd_flag}, 1000, (struct if_dqblk[1]){{0}}",
            "Q_GETNEXTQUOTA": f"0, {cmd_flag}, 1000, (struct if_nextdqblk[1]){{0}}"
        }[syscall_name]
    else:
        arg_str = {
            "Q_SYNC": f"{cmd_flag}, \"\", 0, 0",
            "Q_QUOTAON": f"{cmd_flag}, \"/dev/null\", 1000, \"/dev/null\"",
            "Q_QUOTAOFF": f"{cmd_flag}, \"/dev/null\", 1000, 0",
            "Q_GETFMT": f"{cmd_flag}, \"/dev/null\", 1000, (int[1]){{0}}",
            "Q_GETINFO": f"{cmd_flag}, \"/dev/null\", 1000, (struct if_dqinfo[1]){{0}}",
            "Q_SETINFO": f"{cmd_flag}, \"/dev/null\", 1000, (struct if_dqinfo[1]){{0}}",
            "Q_GETQUOTA": f"{cmd_flag}, \"/dev/null\", 1000, (struct if_dqblk[1]){{0}}",
            "Q_SETQUOTA": f"{cmd_flag}, \"/dev/null\", 1000, (struct if_dqblk[1]){{0}}",
            "Q_GETNEXTQUOTA": f"{cmd_flag}, \"/dev/null\", 1000, (struct if_nextdqblk[1]){{0}}"
        }[syscall_name]

    code = f"""{header}
int main() {{
    {syscall_func}({arg_str});
    return 0;
}}
"""
    with open(filepath, "w") as f:
        f.write(code)

for syscall_name, flag_list in commands.items():
    for flag in flag_list:
        generate_test_code(syscall_name, flag, is_fd=False)
        generate_test_code(syscall_name, flag, is_fd=True)
