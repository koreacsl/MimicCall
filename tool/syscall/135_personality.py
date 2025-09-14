import os

template = """#define _GNU_SOURCE
#include <sys/personality.h>
#include <stdio.h>
#include <errno.h>

int main() {
    unsigned long persona_flag = {persona_flag};

    unsigned long old_personality = personality(0xffffffff);
    if (old_personality == -1) {
        perror("personality failed to get current setting");
        return 1;
    }

    unsigned long new_personality = personality(persona_flag);
    if (new_personality == -1) {
        perror("personality failed to set new setting");
        return 1;
    }

    return 0;
}
"""

directory = "./tool/cfiles/135_personality"
os.makedirs(directory, exist_ok=True)

personality_flags = [
    "PER_LINUX",
    "PER_SVR4",
    "PER_SVR3",
    "PER_OSR5",
    "PER_WYSEV386",
    "PER_ISCR4",
    "PER_BSD",
    "PER_XENIX",
    "PER_LINUX32",
    "PER_IRIX32",
    "PER_IRIXN32",
    "PER_IRIX64",
    "PER_RISCOS",
    "PER_SOLARIS",
    "PER_UW7",
    "PER_OSF4",
    "PER_HPUX",
    "ADDR_NO_RANDOMIZE",
    "MMAP_PAGE_ZERO",
    "ADDR_COMPAT_LAYOUT",
    "READ_IMPLIES_EXEC",
    "ADDR_LIMIT_32BIT",
    "SHORT_INODE",
    "WHOLE_SECONDS",
    "STICKY_TIMEOUTS",
    "ADDR_LIMIT_3GB"
]

for i, flag_name in enumerate(personality_flags):
    filename = os.path.join(directory, f"personality_{i}_{flag_name}.c")
    with open(filename, "w") as f:
        f.write(template.replace("{persona_flag}", flag_name).replace("{persona_flag_str}", flag_name))
