import os

def generate_flock_tests():
    output_dir = "./tool/cfiles/73_flock"

    flock_ops = [
        ("flock_shared", "LOCK_SH"),
        ("flock_exclusive", "LOCK_EX"),
        ("flock_unlock", "LOCK_UN"),
        ("flock_shared_nonblock", "LOCK_SH | LOCK_NB"),
        ("flock_exclusive_nonblock", "LOCK_EX | LOCK_NB")
    ]

    for syscall_name, flag in flock_ops:
        c_code = f"""#include <sys/file.h>
#include <fcntl.h>
#include <unistd.h>

int main() {{
    int fd = open("./testfile", O_CREAT | O_RDWR, 0644);
    if (fd == -1) return 1;

    int result = flock(fd, {flag});
    
    close(fd);
    return result;
}}
"""
        filename = f"{output_dir}/{syscall_name}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    output_dir = "./tool/cfiles/73_flock"
    os.makedirs(output_dir, exist_ok=True)
    generate_flock_tests()
