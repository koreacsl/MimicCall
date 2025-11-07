
import os

def generate_perf_event_open_tests():
    output_dir = "./tool/cfiles/298_perf_event_open"
    os.makedirs(output_dir, exist_ok=True)

    attrs = {
        "hw_cpu_cycles": "struct perf_event_attr attr = { .type = PERF_TYPE_HARDWARE, .config = PERF_COUNT_HW_CPU_CYCLES };",
        "sw_cpu_clock": "struct perf_event_attr attr = { .type = PERF_TYPE_SOFTWARE, .config = PERF_COUNT_SW_CPU_CLOCK };",
        "hw_cache_misses": "struct perf_event_attr attr = { .type = PERF_TYPE_HW_CACHE, .config = (PERF_COUNT_HW_CACHE_L1D | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16)) };"
    }

    flags = {
        "none": "0",
        "fd_no_group": "PERF_FLAG_FD_NO_GROUP",
        "fd_cloexec": "PERF_FLAG_FD_CLOEXEC"
    }

    for attr_name, attr_init in attrs.items():
        for flag_name, flag_value in flags.items():
            c_code = f"""#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/perf_event.h>
#include <string.h>

#ifndef SYS_perf_event_open
#define SYS_perf_event_open 298
#endif

int main() {{
    {attr_init}
    attr.size = sizeof(struct perf_event_attr);
    attr.disabled = 1;

    int fd = syscall(SYS_perf_event_open, &attr, 0, -1, -1, {flag_value});
    
    if (fd != -1) {{
        close(fd);
    }}

    return 0;
}}
"""
            filename = os.path.join(output_dir, f"perf_event_open_{attr_name}_{flag_name}.c")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(c_code)

if __name__ == "__main__":
    generate_perf_event_open_tests()
