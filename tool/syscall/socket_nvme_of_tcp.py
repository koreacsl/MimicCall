import os
from textwrap import dedent

OUT = "./tool/cfiles/socket_nvme_of_tcp"
os.makedirs(OUT, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <arpa/inet.h>
#include <linux/socket.h>
#include <linux/net.h>

#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 02000000
#endif
#ifndef SOCK_NONBLOCK
#define SOCK_NONBLOCK 00004000
#endif
#ifndef NVME_TCP_DISC_PORT
#define NVME_TCP_DISC_PORT 8009
#endif

static int mk_tcp(void){
    int s = socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC|SOCK_NONBLOCK, 0);
    if (s < 0) return -1;
    struct sockaddr_in a;
    memset(&a, 0, sizeof(a));
    a.sin_family = AF_INET;
    a.sin_port = htons(NVME_TCP_DISC_PORT);
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    (void)connect(s, (struct sockaddr*)&a, sizeof(a));
    return s;
}

static void try_sendto(int s, const void* p, size_t n){
    (void)sendto(s, p, n, 0, NULL, 0);
}

static void try_recvmsg(int s){
    char buf[64];
    struct iovec iov = { .iov_base = buf, .iov_len = sizeof(buf) };
    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    (void)recvmsg(s, &msg, 0);
}
""").lstrip()

def write_c(name: str, body: str):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(body)

write_c("nvme_tcp_icreq.c", COMMON + r"""
int main(void){
    int s = mk_tcp();
    if (s < 0) return 0;

    struct nvme_tcp_icreq_pdu p;
    memset(&p, 0, sizeof(p));
    p.hdr.type = nvme_tcp_icreq;
    p.hdr.hlen = sizeof(p);
    p.hdr.plen = sizeof(p);
    try_sendto(s, &p, sizeof(p));

    close(s);
    return 0;
}
""")

write_c("nvme_tcp_icresp.c", COMMON + r"""
int main(void){
    int s = mk_tcp();
    if (s < 0) return 0;

    struct nvme_tcp_icresp_pdu p;
    memset(&p, 0, sizeof(p));
    p.hdr.type = nvme_tcp_icresp;
    p.hdr.hlen = sizeof(p);
    p.hdr.plen = sizeof(p);
    try_sendto(s, &p, sizeof(p));

    close(s);
    return 0;
}
""")

write_c("nvme_tcp_cmd.c", COMMON + r"""
int main(void){
    int s = mk_tcp();
    if (s < 0) return 0;

    struct nvme_tcp_cmd_pdu p;
    memset(&p, 0, sizeof(p));
    p.hdr.type = nvme_tcp_cmd;
    p.hdr.hlen = sizeof(p);
    p.hdr.plen = sizeof(p);
    try_sendto(s, &p, sizeof(p));

    close(s);
    return 0;
}
""")

write_c("nvme_tcp_rsp.c", COMMON + r"""
int main(void){
    int s = mk_tcp();
    if (s < 0) return 0;

    struct nvme_tcp_rsp_pdu p;
    memset(&p, 0, sizeof(p));
    p.hdr.type = nvme_tcp_rsp;
    p.hdr.hlen = sizeof(p);
    p.hdr.plen = sizeof(p);
    try_sendto(s, &p, sizeof(p));

    close(s);
    return 0;
}
""")

write_c("nvme_tcp_r2t.c", COMMON + r"""
int main(void){
    int s = mk_tcp();
    if (s < 0) return 0;

    struct nvme_tcp_r2t_pdu p;
    memset(&p, 0, sizeof(p));
    p.hdr.type = nvme_tcp_r2t;
    p.hdr.hlen = sizeof(p);
    p.hdr.plen = sizeof(p);
    try_sendto(s, &p, sizeof(p));

    close(s);
    return 0;
}
""")

write_c("nvme_tcp_data_h2c.c", COMMON + r"""
int main(void){
    int s = mk_tcp();
    if (s < 0) return 0;

    struct nvme_tcp_data_pdu p;
    memset(&p, 0, sizeof(p));
    p.hdr.type = nvme_tcp_h2c_data;
    p.hdr.hlen = sizeof(p);
    p.hdr.plen = sizeof(p);
    try_sendto(s, &p, sizeof(p));

    close(s);
    return 0;
}
""")

write_c("nvme_tcp_data_c2h.c", COMMON + r"""
int main(void){
    int s = mk_tcp();
    if (s < 0) return 0;

    struct nvme_tcp_data_pdu p;
    memset(&p, 0, sizeof(p));
    p.hdr.type = nvme_tcp_c2h_data;
    p.hdr.hlen = sizeof(p);
    p.hdr.plen = sizeof(p);
    try_sendto(s, &p, sizeof(p));

    close(s);
    return 0;
}
""")

write_c("nvme_of_msg_min.c", COMMON + r"""
int main(void){
    int s = mk_tcp();
    if (s < 0) return 0;

    unsigned char buf[64];
    memset(buf, 0, sizeof(buf));
    try_sendto(s, buf, sizeof(buf));

    close(s);
    return 0;
}
""")

write_c("nvme_tcp_recv.c", COMMON + r"""
int main(void){
    int s = mk_tcp();
    if (s < 0) return 0;
    try_recvmsg(s);
    close(s);
    return 0;
}
""")
