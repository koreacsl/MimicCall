import os

output_dir = "./tool/cfiles/309_getcpu"
os.makedirs(output_dir, exist_ok=True)

common_headers = """\
#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <stdint.h>

#ifndef SYS_getcpu
#define SYS_getcpu 309
#endif
"""

def write_c_file(name, content):
    with open(os.path.join(output_dir, f"{name}.c"), "w") as f:
        f.write(content)

def generate_getcpu_tests():
    for use_cpup in [True, False]:
        for use_nodep in [True, False]:
            for use_cache in [True, False]:
                suffix = []
                if use_cpup: suffix.append("cpup")
                if use_nodep: suffix.append("nodep")
                if use_cache: suffix.append("cache")
                if not suffix:
                    suffix.append("null")
                name = f"getcpu_{'_'.join(suffix)}"

                body = ""
                args = []

                if use_cpup:
                    body += "    int cpu = -1;\n"
                    args.append("&cpu")
                else:
                    args.append("0")

                if use_nodep:
                    body += "    int node = -1;\n"
                    args.append("&node")
                else:
                    args.append("0")

                if use_cache:
                    body += "    intptr_t cache[16] = {0};\n"
                    args.append("cache")
                else:
                    args.append("0")

                syscall_line = f"    syscall(SYS_getcpu, {', '.join(args)});\n"

                content = f"""{common_headers}
int main() {{
{body}{syscall_line}    return 0;
}}
"""
                write_c_file(name, content)

generate_getcpu_tests()
