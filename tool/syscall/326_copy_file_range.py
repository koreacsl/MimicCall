import os

def generate_copy_file_range_tests():
    output_dir = "./tool/cfiles/326_copy_file_range"
    tests = [
        ("test_copy_file_range_null_offset", "NULL", "NULL"),
        ("test_copy_file_range_with_offset", "&in_offset", "&out_offset"),
        ("test_copy_file_range_partial", "NULL", "NULL", 512),
        ("test_copy_file_range_large", "NULL", "NULL", 4096)
    ]
    
    for syscall_name, off_in, off_out, *length in tests:
        len_bytes = length[0] if length else 1024
        c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/syscall.h>

int main() {{
    int fd_in = open("testfile_in", O_CREAT | O_WRONLY, 0644);
    int fd_out = open("testfile_out", O_CREAT | O_WRONLY, 0644);
    if (fd_in == -1 || fd_out == -1) return 1;

    write(fd_in, "ABCD", 4);
    lseek(fd_in, 0, SEEK_SET);

    off_t in_offset = 0, out_offset = 0;
    if (syscall(SYS_copy_file_range, fd_in, {off_in}, fd_out, {off_out}, {len_bytes}, 0) == -1) return 1;

    close(fd_in);
    close(fd_out);
    unlink("testfile_in");
    unlink("testfile_out");
    return 0;
}}
"""
        
        filename = f"{output_dir}/{syscall_name}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    output_dir = "./tool/cfiles/326_copy_file_range"
    os.makedirs(output_dir, exist_ok=True)
    generate_copy_file_range_tests()
