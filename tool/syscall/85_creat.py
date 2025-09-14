import os

def generate_creat_tests():
    output_dir = "./tool/cfiles/85_creat"
    modes = [
        ("test_creat_400", "S_IRUSR"),
        ("test_creat_600", "S_IRUSR | S_IWUSR"),
        ("test_creat_700", "S_IRUSR | S_IWUSR | S_IXUSR"),
        ("test_creat_644", "S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH"),
        ("test_creat_755", "S_IRUSR | S_IWUSR | S_IXUSR | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH"),
        ("test_creat_777", "S_IRUSR | S_IWUSR | S_IXUSR | S_IRGRP | S_IWGRP | S_IXGRP | S_IROTH | S_IWOTH | S_IXOTH")
    ]
    
    for syscall_name, mode in modes:
        c_code = f"""#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

int main() {{
    int fd = syscall(SYS_creat, "testfile", {mode});
    if (fd == -1) return 1;
    close(fd);
    unlink("testfile");
    return 0;
}}
""" 
        filename = f"{output_dir}/{syscall_name}.c"
        with open(filename, "w") as f:
            f.write(c_code)

if __name__ == "__main__":
    output_dir = "./tool/cfiles/85_creat"
    os.makedirs(output_dir, exist_ok=True)
    generate_creat_tests()
