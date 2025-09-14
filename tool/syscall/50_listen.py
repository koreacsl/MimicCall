import os

def generate_listen_test():
    output_dir = "./tool/cfiles/50_listen"
    os.makedirs(output_dir, exist_ok=True)

    c_code = """#include <unistd.h>
#include <sys/syscall.h>
#include <sys/socket.h>

#ifndef SYS_socket
#define SYS_socket 41
#endif

#ifndef SYS_listen
#define SYS_listen 50
#endif

int main() {
    int sockfd = syscall(SYS_socket, AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) {
        return 1;
    }

    int result = syscall(SYS_listen, sockfd, 10);

    close(sockfd);

    if (result == -1) {
        return 1;
    }

    return 0;
}
"""
    filename = f"{output_dir}/listen_0.c"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_listen_test()
