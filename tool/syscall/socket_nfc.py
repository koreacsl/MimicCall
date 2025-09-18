import os
from textwrap import dedent

OUT = "./tool/cfiles/socket_nfc"
os.makedirs(OUT, exist_ok=True)

COMMON = dedent(r"""
#define _GNU_SOURCE
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <linux/net.h>
#include <linux/nfc.h>

#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 02000000
#endif
#ifndef SOCK_NONBLOCK
#define SOCK_NONBLOCK 04000
#endif
#ifndef AF_NFC
#define AF_NFC 39
#endif
#ifndef NFC_SOCKPROTO_LLCP
#define NFC_SOCKPROTO_LLCP 0
#endif
#ifndef NFC_SOCKPROTO_RAW
#define NFC_SOCKPROTO_RAW 1
#endif
#ifndef NFC_PROTO_NFC_DEP
#define NFC_PROTO_NFC_DEP 0
#endif
#ifndef SOL_NFC
#define SOL_NFC 280
#endif

static int set_nonblock(int s){
    int f = fcntl(s, F_GETFL, 0);
    if (f >= 0) (void)fcntl(s, F_SETFL, f|O_NONBLOCK);
    return s;
}

static int nfc_llcp_open(int type){
    int s = socket(AF_NFC, type|SOCK_CLOEXEC, NFC_SOCKPROTO_LLCP);
    if (s >= 0) set_nonblock(s);
    return s;
}

static int nfc_raw_open(int type){
    int s = socket(AF_NFC, type|SOCK_CLOEXEC, NFC_SOCKPROTO_RAW);
    if (s >= 0) set_nonblock(s);
    return s;
}

static void do_bind_llcp(int s){
    struct sockaddr_nfc_llcp a;
    memset(&a, 0, sizeof(a));
    a.sa_family = AF_NFC;
    a.dev_idx = 0;
    a.target_idx = 0;
    a.nfc_protocol = NFC_PROTO_NFC_DEP; /* A valid value */
    a.dsap = 0;
    a.ssap = 0;
    a.service_name[0] = 0;
    a.service_name_len = 0;
    (void)bind(s, (struct sockaddr*)&a, sizeof(a));
}

static void do_connect_llcp(int s){
    struct sockaddr_nfc_llcp a;
    memset(&a, 0, sizeof(a));
    a.sa_family = AF_NFC;
    a.dev_idx = 0;
    a.target_idx = 0;
    a.nfc_protocol = NFC_PROTO_NFC_DEP;
    a.dsap = 0;
    a.ssap = 0;
    (void)connect(s, (struct sockaddr*)&a, sizeof(a));
}

static void do_sendmsg_llcp(int s){
    struct sockaddr_nfc_llcp a;
    memset(&a, 0, sizeof(a));
    a.sa_family = AF_NFC;
    a.dev_idx = 0;
    a.target_idx = 0;
    a.nfc_protocol = NFC_PROTO_NFC_DEP;
    a.dsap = 0;
    a.ssap = 0;

    char data = 0;
    struct iovec iov = { .iov_base = &data, .iov_len = 1 };
    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    msg.msg_name = &a;
    msg.msg_namelen = sizeof(a);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    (void)sendmsg(s, &msg, 0);
}

static void do_sendmmsg_llcp(int s){
    struct sockaddr_nfc_llcp a;
    memset(&a, 0, sizeof(a));
    a.sa_family = AF_NFC;
    a.dev_idx = 0;
    a.target_idx = 0;
    a.nfc_protocol = NFC_PROTO_NFC_DEP;
    a.dsap = 0;
    a.ssap = 0;

    char b = 0;
    struct iovec iov = { .iov_base = &b, .iov_len = 1 };
    struct msghdr m;
    memset(&m, 0, sizeof(m));
    m.msg_name = &a;
    m.msg_namelen = sizeof(a);
    m.msg_iov = &iov;
    m.msg_iovlen = 1;

    struct mmsghdr mm;
    memset(&mm, 0, sizeof(mm));
    mm.msg_hdr = m;
    mm.msg_len = 0;
    (void)sendmmsg(s, &mm, 1, 0);
}

static void do_accept4_try(int s){
    (void)accept4(s, NULL, NULL, SOCK_NONBLOCK|SOCK_CLOEXEC);
}

static void do_setsockopt_llcp_min(int s){
    int v = 0;
    (void)setsockopt(s, SOL_NFC, NFC_LLCP_RW, &v, sizeof(v));
    (void)setsockopt(s, SOL_NFC, NFC_LLCP_MIUX, &v, sizeof(v));
}

static void do_getsockopt_llcp_all(int s){
    int buf[8]; socklen_t l;
    l = sizeof(buf); (void)getsockopt(s, SOL_NFC, NFC_LLCP_RW, buf, &l);
    l = sizeof(buf); (void)getsockopt(s, SOL_NFC, NFC_LLCP_MIUX, buf, &l);
    l = sizeof(buf); (void)getsockopt(s, SOL_NFC, NFC_LLCP_REMOTE_MIU, buf, &l);
    l = sizeof(buf); (void)getsockopt(s, SOL_NFC, NFC_LLCP_REMOTE_LTO, buf, &l);
    l = sizeof(buf); (void)getsockopt(s, SOL_NFC, NFC_LLCP_REMOTE_RW, buf, &l);
}

static void do_connect_raw(int s){
    struct sockaddr_nfc a;
    memset(&a, 0, sizeof(a));
    a.sa_family = AF_NFC;
    a.dev_idx = 0;
    a.target_idx = 0;
    a.nfc_protocol = NFC_PROTO_NFC_DEP;
    (void)connect(s, (struct sockaddr*)&a, sizeof(a));
}
""").lstrip()

def write_c(name: str, body: str):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(body)

for tname, tval in [("stream", "SOCK_STREAM"), ("dgram", "SOCK_DGRAM"), ("raw", "SOCK_RAW")]:
    write_c(f"nfc_llcp_basic_{tname}.c", COMMON + f"""
int main(void){{
    int s = nfc_llcp_open({tval});
    if (s < 0) return 0;
    do_bind_llcp(s);
    do_connect_llcp(s);
    do_setsockopt_llcp_min(s);
    do_getsockopt_llcp_all(s);
    do_sendmsg_llcp(s);
    do_sendmmsg_llcp(s);
    do_accept4_try(s);
    close(s);
    return 0;
}}
""")

for tname, tval in [("seqpacket", "SOCK_SEQPACKET"), ("raw", "SOCK_RAW")]:
    write_c(f"nfc_raw_basic_{tname}.c", COMMON + f"""
int main(void){{
    int s = nfc_raw_open({tval});
    if (s < 0) return 0;
    do_connect_raw(s);
    close(s);
    return 0;
}}
""")

write_c("nfc_llcp_opts.c", COMMON + r"""
int main(void){
    int s = nfc_llcp_open(SOCK_STREAM);
    if (s < 0) return 0;
    do_setsockopt_llcp_min(s);
    do_getsockopt_llcp_all(s);
    close(s);
    return 0;
}
""")
