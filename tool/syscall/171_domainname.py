import os

template = """#define _GNU_SOURCE
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <sys/param.h>
#include <sys/syscall.h>

int main() {
    char domain_name[65];

    if (getdomainname(domain_name, sizeof(domain_name) - 1) == -1) {
        perror("getdomainname failed");
        return 1;
    }
    domain_name[sizeof(domain_name) - 1] = '\\0';

    if (syscall(SYS_setdomainname, domain_name, strlen(domain_name)) == -1) {
        perror("setdomainname failed");
        return 1;
    }

    if (getdomainname(domain_name, sizeof(domain_name) - 1) == -1) {
        perror("getdomainname failed after setdomainname");
        return 1;
    }

    return 0;
}
"""

directory = "./tool/cfiles/171_domainname"
os.makedirs(directory, exist_ok=True)

filename = os.path.join(directory, f"domainname_0.c")

with open(filename, "w") as f:
    f.write(template)
