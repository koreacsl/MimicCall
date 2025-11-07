import os
from textwrap import dedent

OUTPUT_DIR = "./tool/cfiles/hafnium"
os.makedirs(OUTPUT_DIR, exist_ok=True)

COMMON_HEADERS = dedent(r"""
    #include <stdint.h>
    #include <unistd.h>
    #include <string.h>
    #include <errno.h>
    #include <sys/types.h>
    #include <sys/socket.h>
    #include <linux/socket.h>
    #include <linux/net.h>
    #include <sys/uio.h>
    #include <sys/time.h>

    #ifndef AF_ECONET
    #define AF_ECONET 19
    #endif

    #ifndef AF_HF
    #define AF_HF AF_ECONET
    #endif

    struct sockaddr_hf {
        uint16_t family;
        int32_t  vm_id;
        int64_t  port;
    };

    static int make_sock(void) {
        int s = socket(AF_HF, SOCK_DGRAM, 0);
        if (s < 0) return -1;
        return s;
    }
""").lstrip()

CONNECT_BODY = dedent(r"""
    int main(void) {
        int s = make_sock();
        if (s < 0) return 0;

        struct sockaddr_hf addr;
        memset(&addr, 0, sizeof(addr));
        addr.family = AF_HF;
        addr.vm_id = 1;
        addr.port = 1;

        (void)connect(s, (struct sockaddr*)&addr, sizeof(addr));
        close(s);
        return 0;
    }
""").lstrip()

SEND_TEMPLATE = r"""
{headers}
int main(void) {{
    int s = make_sock();
    if (s < 0) return 0;

    struct sockaddr_hf addr;
    memset(&addr, 0, sizeof(addr));
    addr.family = AF_HF;
    addr.vm_id = 1;
    addr.port = 1;

    (void)connect(s, (struct sockaddr*)&addr, sizeof(addr));

    char buf[1] = {{0}};
    struct iovec iov;
    iov.iov_base = buf;
    iov.iov_len  = sizeof(buf);

    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    msg.msg_name    = &addr;
    msg.msg_namelen = sizeof(addr);
    msg.msg_iov     = &iov;
    msg.msg_iovlen  = 1;

    (void)sendmsg(s, &msg, {flag});
    close(s);
    return 0;
}}
""".strip()

RECV_TEMPLATE = r"""
{headers}
int main(void) {{
    int s = make_sock();
    if (s < 0) return 0;

    struct timeval tv;
    tv.tv_sec = 0;
    tv.tv_usec = 1000;
    (void)setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    char buf[1];
    struct iovec iov;
    iov.iov_base = buf;
    iov.iov_len  = sizeof(buf);

    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    msg.msg_iov     = &iov;
    msg.msg_iovlen  = 1;

    (void)recvmsg(s, &msg, {flag});
    close(s);
    return 0;
}}
""".strip()

send_flags = [
    "MSG_CONFIRM", "MSG_DONTROUTE", "MSG_DONTWAIT", "MSG_EOR", "MSG_MORE",
    "MSG_NOSIGNAL", "MSG_OOB", "MSG_PROBE", "MSG_BATCH", "MSG_FASTOPEN", "MSG_ZEROCOPY"
]

recv_flags = [
    "MSG_CMSG_CLOEXEC", "MSG_DONTWAIT", "MSG_ERRQUEUE", "MSG_OOB",
    "MSG_PEEK", "MSG_TRUNC", "MSG_WAITALL", "MSG_WAITFORONE"
]

with open(os.path.join(OUTPUT_DIR, "socket_connect.c"), "w") as f:
    f.write(COMMON_HEADERS + "\n" + CONNECT_BODY)

for fl in send_flags:
    fname = f"send_{fl.lower().replace('msg_','')}.c"
    with open(os.path.join(OUTPUT_DIR, fname), "w") as f:
        f.write(SEND_TEMPLATE.format(headers=COMMON_HEADERS, flag=fl))

for fl in recv_flags:
    fname = f"recv_{fl.lower().replace('msg_','')}.c"
    with open(os.path.join(OUTPUT_DIR, fname), "w") as f:
        f.write(RECV_TEMPLATE.format(headers=COMMON_HEADERS, flag=fl))