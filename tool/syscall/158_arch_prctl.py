import os
from itertools import combinations, product

arch_output_dir = "./tool/cfiles/158_arch_prctl"
os.makedirs(arch_output_dir, exist_ok=True)

arch_header = '''#define _GNU_SOURCE
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdint.h>

#define ARCH_SET_GS 4097         
#define ARCH_SET_FS 4098         
#define ARCH_GET_FS 4099         
#define ARCH_GET_GS 4100         
#define ARCH_GET_CPUID 4113      
#define ARCH_SET_CPUID 4114      
#define ARCH_GET_XCOMP_SUPP 4129 
#define ARCH_GET_XCOMP_PERM 4130 
#define ARCH_REQ_XCOMP_PERM 4131 
#define ARCH_GET_XCOMP_GUEST_PERM 4132 
#define ARCH_REQ_XCOMP_GUEST_PERM 4133 
#define ARCH_MAP_VDSO_X32 8193   
#define ARCH_MAP_VDSO_32 8194    
#define ARCH_MAP_VDSO_64 8195    
#define ARCH_GET_UNTAG_MASK 16385  
#define ARCH_GET_MAX_TAG_BITS 16387 
#define ARCH_ENABLE_TAGGED_ADDR 16386 
#define ARCH_FORCE_TAGGED_SVA 16388 

#define ARCH_SHSTK_ENABLE 20481   
#define ARCH_SHSTK_DISABLE 20482  
#define ARCH_SHSTK_LOCK 20483     
#define ARCH_SHSTK_UNLOCK 20484   
#define ARCH_SHSTK_STATUS 20485   

#define ARCH_SHSTK_SHSTK 1
#define ARCH_SHSTK_WRSS  2
'''


def write_arch_test(filename, body):
    with open(os.path.join(arch_output_dir, filename), "w") as f:
        f.write(arch_header + body)
    
read_ptr = "(intptr_t*)buf"
write_ptr = "1"

read_tests = [
    ("ARCH_GET_FS", "ARCH_GET_FS", read_ptr),
    ("ARCH_GET_GS", "ARCH_GET_GS", read_ptr),
    ("ARCH_GET_XCOMP_SUPP", "ARCH_GET_XCOMP_SUPP", "(int64_t*)buf"),
    ("ARCH_GET_XCOMP_PERM", "ARCH_GET_XCOMP_PERM", "(int64_t*)buf"),
    ("ARCH_GET_XCOMP_GUEST_PERM", "ARCH_GET_XCOMP_GUEST_PERM", "(int64_t*)buf"),
    ("ARCH_GET_UNTAG_MASK", "ARCH_GET_UNTAG_MASK", read_ptr),
    ("ARCH_GET_MAX_TAG_BITS", "ARCH_GET_MAX_TAG_BITS", read_ptr),
    ("ARCH_SHSTK_STATUS", "ARCH_SHSTK_STATUS", read_ptr),
]

for name, cmd, arg in read_tests:
    body = f'''
int main() {{
    intptr_t buf = 0;
    syscall(SYS_arch_prctl, {cmd}, {arg});
    return 0;
}}
'''
    write_arch_test(f"arch_prctl_{name.lower()}.c", body)

write_tests = [
    ("ARCH_SET_GS", "ARCH_SET_GS", write_ptr),
    ("ARCH_SET_FS", "ARCH_SET_FS", write_ptr),
    ("ARCH_MAP_VDSO_X32", "ARCH_MAP_VDSO_X32", write_ptr),
    ("ARCH_MAP_VDSO_32", "ARCH_MAP_VDSO_32", write_ptr),
    ("ARCH_MAP_VDSO_64", "ARCH_MAP_VDSO_64", write_ptr),
    ("ARCH_ENABLE_TAGGED_ADDR", "ARCH_ENABLE_TAGGED_ADDR", "3"),
    ("ARCH_REQ_XCOMP_PERM", "ARCH_REQ_XCOMP_PERM", "4"),
    ("ARCH_REQ_XCOMP_GUEST_PERM", "ARCH_REQ_XCOMP_GUEST_PERM", "5"),
    ("ARCH_SET_CPUID", "ARCH_SET_CPUID", "1"),
    ("ARCH_FORCE_TAGGED_SVA", "ARCH_FORCE_TAGGED_SVA", "0"),
]

for name, cmd, arg in write_tests:
    body = f'''
int main() {{
    syscall(SYS_arch_prctl, {cmd}, {arg});
    return 0;
}}
'''
    write_arch_test(f"arch_prctl_{name.lower()}.c", body)

shadow_stack_flags = ["ARCH_SHSTK_SHSTK", "ARCH_SHSTK_WRSS"]
for flag_combo in sum([list(combinations(shadow_stack_flags, r)) for r in range(1, len(shadow_stack_flags)+1)], []):
    flag_expr = " | ".join(flag_combo)
    for cmd_name in ["ENABLE", "DISABLE", "LOCK", "UNLOCK"]:
        cmd_macro = f"ARCH_SHSTK_{cmd_name}"
        fname = f"arch_prctl_shstk_{cmd_name.lower()}_{'_'.join(flag_combo).lower()}.c"
        body = f'''
int main() {{
    syscall(SYS_arch_prctl, {cmd_macro}, {flag_expr});
    return 0;
}}
'''
        write_arch_test(fname, body)
