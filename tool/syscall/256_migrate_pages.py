
import os

def generate_migrate_pages_tests():
    output_dir = "./tool/cfiles/256_migrate_pages"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <numaif.h>
#include <sys/mman.h>
#include <dirent.h>
#include <string.h>
#include <stdio.h>

#ifndef SYS_migrate_pages
#define SYS_migrate_pages 256
#endif

int get_available_nodes(unsigned long *nodemask, int max_nodes) {
    DIR *dir = opendir("/sys/devices/system/node/");
    if (!dir) return -1;

    struct dirent *entry;
    int highest_node = -1;
    *nodemask = 0;

    while ((entry = readdir(dir)) != NULL) {
        int node_id;
        if (sscanf(entry->d_name, "node%d", &node_id) == 1) {
            if (node_id >= 0 && node_id < max_nodes) {
                *nodemask |= (1UL << node_id);
                if (node_id > highest_node) {
                    highest_node = node_id;
                }
            }
        }
    }
    closedir(dir);
    return highest_node;
}

int main() {
    long page_size = sysconf(_SC_PAGESIZE);
    if (page_size < 0) return 1;
    
    void *addr = mmap(NULL, page_size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) return 1;

    memset(addr, 0, page_size);

    unsigned long max_node_count = 256;
    unsigned long old_nodes = 0;
    int max_node_id = get_available_nodes(&old_nodes, max_node_count);
    if (max_node_id < 0) {
        munmap(addr, page_size);
        return 0;
    }
    
    unsigned long new_nodes = old_nodes;

    if (syscall(SYS_migrate_pages, 0, max_node_count, &old_nodes, &new_nodes) == -1) {
        munmap(addr, page_size);
        return 1;
    }

    munmap(addr, page_size);
    return 0;
}
"""
    filename = os.path.join(output_dir, "migrate_pages.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_migrate_pages_tests()
