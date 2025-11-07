import os

output_dir = "./tool/cfiles/334_rseq"
os.makedirs(output_dir, exist_ok=True)

template = """#define _GNU_SOURCE
#include <errno.h>
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/syscall.h>

#define RSEQ_CS_FLAG_NO_RESTART_ON_PREEMPT 1
#define RSEQ_CS_FLAG_NO_RESTART_ON_SIGNAL 2
#define RSEQ_CS_FLAG_NO_RESTART_ON_MIGRATE 4

struct rseq_cs {{
    int32_t version;               
    int32_t flags;                 
    int64_t start_ip;
    int64_t post_commit_offset;
    int64_t abort_ip;
}} __attribute__((aligned(32)));

typedef struct rseq {{
    int32_t cpu_id_start;          
    int32_t cpu_id;                
    struct rseq_cs *rseq_cs;       
    int32_t flags;                 
}} rseq_t __attribute__((aligned(32)));

int main() {{
    rseq_t rseq = {{ 0, 0, NULL, 0 }};

    {extra}

    int ret = syscall(SYS_rseq, {ptr}, {length}, {flags_arg}, {sig});   
    if (ret == -1) perror("rseq");
    return 0;
}}
"""

tests = [
    {
        "name": "ptr",
        "ptr": "&rseq",
        "length": "sizeof(rseq_t)",
        "flags_arg": "NULL",
        "sig": "0",
        "extra": ""
    },
    {
        "name": "len",
        "ptr": "&rseq",
        "length": "sizeof(rseq_t)",
        "flags_arg": "NULL",
        "sig": "0",
        "extra": ""
    },
    {
        "name": "flags",
        "ptr": "&rseq",
        "length": "sizeof(rseq_t)",
        "flags_arg": "&flag",
        "sig": "0",
        "extra": "int flag = 1;"
    },
    {
        "name": "sig",
        "ptr": "&rseq",
        "length": "sizeof(rseq_t)",
        "flags_arg": "NULL",
        "sig": "0",
        "extra": ""
    }
]

for t in tests:
    fname = f"rseq_{t['name']}.c"
    with open(os.path.join(output_dir, fname), "w") as f:
        f.write(template.format(**t))
