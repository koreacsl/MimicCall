import os

c_code = """#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <sys/syscall.h>

int main(void) {
    int fd;
    char buffer[32] = {0};
    const char *filename = "testfile.txt";
    const char *content = "1";

    fd = open(filename, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        return 1;
    }
    write(fd, content, strlen(content));
    close(fd);

    fd = open(filename, O_RDONLY);
    if (fd == -1) {
        remove(filename);
        return 1;
    }
    syscall(SYS_read, fd, buffer, sizeof(buffer) - 1);
    close(fd);

    remove(filename);

    return 0;
}
"""

output_dir = "./tool/cfiles/0_read"
output_filename = "read_0.c"
output_path = os.path.join(output_dir, output_filename)

try:
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(c_code)

except OSError as e:
    print(f"Error creating directory or file: {e}")
except IOError as e:
    print(f"Error writing to file: {e}")