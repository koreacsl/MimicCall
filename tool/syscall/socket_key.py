import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_key"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/uio.h>

#include <linux/socket.h>
#include <linux/net.h>
#include <linux/pfkeyv2.h>
#include <linux/ipsec.h>

#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 02000000
#endif

struct sadb_msg_hdr {
    uint8_t  sadb_msg_version;
    uint8_t  sadb_msg_type;
    uint8_t  sadb_msg_errno;
    uint8_t  sadb_msg_satype;
    uint16_t sadb_msg_len;
    uint16_t sadb_msg_reserved;
    uint32_t sadb_msg_seq;
    uint32_t sadb_msg_pid;
} __attribute__((packed));

struct sadb_sa_min {
    uint16_t sadb_len;          
    uint16_t sadb_exttype;     
    uint32_t sadb_sa_spi;     
    uint8_t  sadb_sa_replay;  
    uint8_t  sadb_sa_state;  
    uint8_t  sadb_sa_auth;      
    uint8_t  sadb_sa_encrypt;  
    uint32_t sadb_sa_flags;     
} __attribute__((packed));

static int make_key_sock(void) {
    int s = socket(AF_KEY, SOCK_RAW | SOCK_CLOEXEC, PF_KEY_V2);
    if (s >= 0) {
        int fl = fcntl(s, F_GETFL, 0);
        if (fl >= 0) fcntl(s, F_SETFL, fl | O_NONBLOCK);
    }
    return s;
}

static void send_sa_flags(uint32_t flags) {
    int s = make_key_sock();
    if (s < 0) return;

    struct {
        struct sadb_msg_hdr msg;
        struct sadb_sa_min  sa;
    } __attribute__((packed)) pkt;

    memset(&pkt, 0, sizeof(pkt));
    pkt.msg.sadb_msg_version = PF_KEY_V2;
    pkt.msg.sadb_msg_type    = SADB_RESERVED; 
    pkt.msg.sadb_msg_satype  = SADB_SATYPE_UNSPEC;
    pkt.msg.sadb_msg_len     = (sizeof(pkt) / 8);

    pkt.sa.sadb_len       = (sizeof(struct sadb_sa_min) / 8);
    pkt.sa.sadb_exttype   = SADB_EXT_SA;
    pkt.sa.sadb_sa_flags  = flags;

    struct iovec iov = {
        .iov_base = &pkt,
        .iov_len  = sizeof(pkt),
    };
    struct msghdr mh = {0};
    mh.msg_iov    = &iov;
    mh.msg_iovlen = 1;

    (void)sendmsg(s, &mh, 0);
    close(s);
}
""").lstrip()

FLAGS = [
    ("SADB_SAFLAGS_PFS",         "SADB_SAFLAGS_PFS"),
    ("SADB_SAFLAGS_NOPMTUDISC",  "SADB_SAFLAGS_NOPMTUDISC"),
    ("SADB_SAFLAGS_DECAP_DSCP",  "SADB_SAFLAGS_DECAP_DSCP"),
    ("SADB_SAFLAGS_NOECN",       "SADB_SAFLAGS_NOECN"),
]

def write_test(flag_name_macro: str):
    name = f"sendmsg_key_sa_{flag_name_macro}.c"
    src = COMMON + f"""
int main(void) {{
    send_sa_flags({flag_name_macro});
    return 0;
}}
"""
    with open(os.path.join(OUTDIR, name), "w") as f:
        f.write(src)

for _, macro in FLAGS:
    write_test(macro)

with open(os.path.join(OUTDIR, "sendmsg_key_sa_NONE.c"), "w") as f:
    f.write(COMMON + """
int main(void) {
    send_sa_flags(0);
    return 0;
}
""")