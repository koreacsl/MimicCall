import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_inet_tcp"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <linux/tcp.h>
#include <linux/sockios.h>
#include <linux/tls.h>

#ifndef IPPROTO_TCP
#define IPPROTO_TCP 6
#endif
#ifndef SOL_TCP
#define SOL_TCP IPPROTO_TCP
#endif
#ifndef SOL_MPTCP
#define SOL_MPTCP 284
#endif
#ifndef IPPROTO_MPTCP
#define IPPROTO_MPTCP 262
#endif
#ifndef AF_SMC
#define AF_SMC 43
#endif
#ifndef TCP_FASTOPEN_KEY_LENGTH
#define TCP_FASTOPEN_KEY_LENGTH 16
#endif
#ifndef TCP_MD5SIG_MAXKEYLEN
#define TCP_MD5SIG_MAXKEYLEN 80
#endif
#ifndef TCP_ULP
#define TCP_ULP 31
#endif

static int s4(void){ int s=socket(AF_INET,  SOCK_STREAM, IPPROTO_TCP); if(s<0) return -1; return s; }
static int s6(void){ int s=socket(AF_INET6, SOCK_STREAM, IPPROTO_TCP); if(s<0) return -1; return s; }
static int s4_mptcp(void){ int s=socket(AF_INET,  SOCK_STREAM, IPPROTO_MPTCP); if(s<0) return -1; return s; }
static int s6_mptcp(void){ int s=socket(AF_INET6, SOCK_STREAM, IPPROTO_MPTCP); if(s<0) return -1; return s; }
static int s_smc(void){ int s=socket(AF_SMC, SOCK_STREAM, 0); if(s<0) return -1; return s; }

struct tcp_md5sig_min {
    struct sockaddr_storage tcpm_addr;
    uint8_t  tcpm_flags;
    uint8_t  tcpm_prefixlen;
    uint16_t tcpm_keylen;
    uint32_t __pad;
    uint8_t  tcpm_key[TCP_MD5SIG_MAXKEYLEN];
};

struct tcp_repair_window_min {
    int32_t snd_wl1, snd_wnd, max_window, rcv_wnd, rcv_wup;
};
""").lstrip()

def w(name, src):
    with open(os.path.join(OUTDIR, name), "w") as f:
        f.write(src)

w("socket_v4.c", COMMON + "int main(void){ int s=s4(); if(s>=0) close(s); return 0; }\n")
w("socket_v6.c", COMMON + "int main(void){ int s=s6(); if(s>=0) close(s); return 0; }\n")
w("socket_mptcp_v4.c", COMMON + "int main(void){ int s=s4_mptcp(); if(s>=0) close(s); return 0; }\n")
w("socket_mptcp_v6.c", COMMON + "int main(void){ int s=s6_mptcp(); if(s>=0) close(s); return 0; }\n")
w("socket_smc.c", COMMON + "int main(void){ int s=s_smc(); if(s>=0) close(s); return 0; }\n")

int_opts = [
 "TCP_NODELAY","TCP_MAXSEG","TCP_CORK","TCP_KEEPIDLE","TCP_KEEPINTVL","TCP_KEEPCNT","TCP_SYNCNT",
 "TCP_LINGER2","TCP_DEFER_ACCEPT","TCP_WINDOW_CLAMP","TCP_QUICKACK","TCP_THIN_LINEAR_TIMEOUTS",
 "TCP_THIN_DUPACK","TCP_USER_TIMEOUT","TCP_FASTOPEN","TCP_FASTOPEN_CONNECT","TCP_FASTOPEN_NO_COOKIE",
 "TCP_TIMESTAMP","TCP_NOTSENT_LOWAT","TCP_SAVE_SYN","TCP_INQ"
]

SET_INT_TPL = r"""
{common}
int main(void){{
    int s={sock}(); if(s<0) return 0;
    int v=0;
    (void)setsockopt(s, IPPROTO_TCP, {opt}, &v, sizeof(v));
    close(s); return 0;
}}
""".strip()

GET_INT_TPL = r"""
{common}
int main(void){{
    int s={sock}(); if(s<0) return 0;
    int v=0; socklen_t l=sizeof(v);
    (void)getsockopt(s, IPPROTO_TCP, {opt}, &v, &l);
    close(s); return 0;
}}
""".strip()

for opt in int_opts:
    base = opt.lower()
    w(f"v4_set_{base}.c", SET_INT_TPL.format(common=COMMON, sock="s4", opt=opt))
    w(f"v4_get_{base}.c", GET_INT_TPL.format(common=COMMON, sock="s4", opt=opt))
    w(f"v6_set_{base}.c", SET_INT_TPL.format(common=COMMON, sock="s6", opt=opt))
    w(f"v6_get_{base}.c", GET_INT_TPL.format(common=COMMON, sock="s6", opt=opt))

buf_opts = ["TCP_INFO","TCP_CONGESTION","TCP_ULP","TCP_MD5SIG","TCP_CC_INFO","TCP_SAVED_SYN","TCP_FASTOPEN_KEY"]

SET_BUF_TPL = r"""
{common}
int main(void){{
    int s={sock}(); if(s<0) return 0;
    unsigned char b[1]={{0}};
    (void)setsockopt(s, IPPROTO_TCP, {opt}, b, sizeof(b));
    close(s); return 0;
}}
""".strip()

GET_BUF_TPL = r"""
{common}
int main(void){{
    int s={sock}(); if(s<0) return 0;
    unsigned char b[64]; socklen_t l=sizeof(b);
    (void)getsockopt(s, IPPROTO_TCP, {opt}, b, &l);
    close(s); return 0;
}}
""".strip()

for opt in buf_opts:
    base = opt.lower()
    w(f"v4_get_{base}.c", GET_BUF_TPL.format(common=COMMON, sock="s4", opt=opt))
    w(f"v6_get_{base}.c", GET_BUF_TPL.format(common=COMMON, sock="s6", opt=opt))
    w(f"v4_set_{base}.c", SET_BUF_TPL.format(common=COMMON, sock="s4", opt=opt))
    w(f"v6_set_{base}.c", SET_BUF_TPL.format(common=COMMON, sock="s6", opt=opt))

mptcp_opts = ["MPTCP_INFO","MPTCP_FULL_INFO","MPTCP_TCPINFO","MPTCP_SUBFLOW_ADDRS"]
GET_MPTCP_TPL = r"""
{common}
int main(void){{
    int s={sock}(); if(s<0) return 0;
    unsigned char b[128]; socklen_t l=sizeof(b);
    (void)getsockopt(s, SOL_MPTCP, {opt}, b, &l);
    close(s); return 0;
}}
""".strip()
for opt in mptcp_opts:
    base = opt.lower()
    w(f"mptcp_v4_get_{base}.c", GET_MPTCP_TPL.format(common=COMMON, sock="s4_mptcp", opt=opt))
    w(f"mptcp_v6_get_{base}.c", GET_MPTCP_TPL.format(common=COMMON, sock="s6_mptcp", opt=opt))

ZC_TPL = r"""
{common}
int main(void){{
    int s={sock}(); if(s<0) return 0;
    struct tcp_zerocopy_receive z; memset(&z, 0, sizeof(z));
    socklen_t l = sizeof(z);
    (void)getsockopt(s, IPPROTO_TCP, TCP_ZEROCOPY_RECEIVE, &z, &l);
    close(s); return 0;
}}
""".strip()
w("v4_get_zerocopy_receive.c", ZC_TPL.format(common=COMMON, sock="s4"))
w("v6_get_zerocopy_receive.c", ZC_TPL.format(common=COMMON, sock="s6"))

cc_algs = ["cubic","reno","bic","cdg","dctcp","westwood","highspeed","hybla","htcp","vegas","nv","veno","scalable","lp","yeah","illinois","dctcp-reno","bbr"]
CC_TPL = r"""
{common}
int main(void){{
    int s={sock}(); if(s<0) return 0;
    static const char name[] = "{alg}";
    (void)setsockopt(s, IPPROTO_TCP, TCP_CONGESTION, name, sizeof(name));
    close(s); return 0;
}}
""".strip()
for alg in cc_algs:
    tag = alg.replace("-","_")
    w(f"v4_set_tcp_congestion_{tag}.c", CC_TPL.format(common=COMMON, sock="s4", alg=alg))
    w(f"v6_set_tcp_congestion_{tag}.c", CC_TPL.format(common=COMMON, sock="s6", alg=alg))

w("v4_set_tcp_ulp_tls.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    static const char name[] = "tls";
    (void)setsockopt(s, IPPROTO_TCP, TCP_ULP, name, sizeof(name));
    close(s); return 0;
}
""")
w("v6_set_tcp_ulp_tls.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    static const char name[] = "tls";
    (void)setsockopt(s, IPPROTO_TCP, TCP_ULP, name, sizeof(name));
    close(s); return 0;
}
""")

MD5_TPL = r"""
{common}
int main(void){{
    int s={sock}(); if(s<0) return 0;
    struct tcp_md5sig_min md5; memset(&md5, 0, sizeof(md5));
    (void)setsockopt(s, IPPROTO_TCP, TCP_MD5SIG, &md5, sizeof(md5));
    close(s); return 0;
}}
""".strip()
w("v4_set_tcp_md5sig.c", MD5_TPL.format(common=COMMON, sock="s4"))
w("v6_set_tcp_md5sig.c", MD5_TPL.format(common=COMMON, sock="s6"))

repair_modes = ["TCP_REPAIR_ON","TCP_REPAIR_OFF","TCP_REPAIR_OFF_NO_WP"]
REPAIR_TPL = r"""
{common}
int main(void){{
    int s={sock}(); if(s<0) return 0;
    int v = {mode};
    (void)setsockopt(s, IPPROTO_TCP, TCP_REPAIR, &v, sizeof(v));
    close(s); return 0;
}}
""".strip()
for m in repair_modes:
    tag = m.lower().replace("tcp_repair_","")
    w(f"v4_set_tcp_repair_{tag}.c", REPAIR_TPL.format(common=COMMON, sock="s4", mode=m))
    w(f"v6_set_tcp_repair_{tag}.c", REPAIR_TPL.format(common=COMMON, sock="s6", mode=m))

repair_queues = ["TCP_NO_QUEUE","TCP_RECV_QUEUE","TCP_SEND_QUEUE"]
RQ_TPL = r"""
{common}
int main(void){{
    int s={sock}(); if(s<0) return 0;
    int v = {q};
    (void)setsockopt(s, IPPROTO_TCP, TCP_REPAIR_QUEUE, &v, sizeof(v));
    close(s); return 0;
}}
""".strip()
for q in repair_queues:
    tag = q.lower().replace("tcp_","")
    w(f"v4_set_tcp_repair_queue_{tag}.c", RQ_TPL.format(common=COMMON, sock="s4", q=q))
    w(f"v6_set_tcp_repair_queue_{tag}.c", RQ_TPL.format(common=COMMON, sock="s6", q=q))

w("v4_set_tcp_queue_seq.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    int v=0;
    (void)setsockopt(s, IPPROTO_TCP, TCP_QUEUE_SEQ, &v, sizeof(v));
    close(s); return 0;
}
""")
w("v6_set_tcp_queue_seq.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    int v=0;
    (void)setsockopt(s, IPPROTO_TCP, TCP_QUEUE_SEQ, &v, sizeof(v));
    close(s); return 0;
}
""")

w("v4_set_tcp_repair_options.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    struct { int32_t opt_code; int32_t opt_val; } o = { 1, 0 }; /* TCPOPT_SACK_PERM is not always available */
    (void)setsockopt(s, IPPROTO_TCP, TCP_REPAIR_OPTIONS, &o, sizeof(o));
    close(s); return 0;
}
""")
w("v6_set_tcp_repair_options.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    struct { int32_t opt_code; int32_t opt_val; } o = { 1, 0 }; /* TCPOPT_SACK_PERM is not always available */
    (void)setsockopt(s, IPPROTO_TCP, TCP_REPAIR_OPTIONS, &o, sizeof(o));
    close(s); return 0;
}
""")

RW_GET_TPL = r"""
{common}
int main(void){{
    int s={sock}(); if(s<0) return 0;
    struct tcp_repair_window_min w; socklen_t l=sizeof(w);
    (void)getsockopt(s, IPPROTO_TCP, TCP_REPAIR_WINDOW, &w, &l);
    close(s); return 0;
}}
""".strip()
RW_SET_TPL = r"""
{common}
int main(void){{
    int s={sock}(); if(s<0) return 0;
    struct tcp_repair_window_min w; memset(&w,0,sizeof(w));
    (void)setsockopt(s, IPPROTO_TCP, TCP_REPAIR_WINDOW, &w, sizeof(w));
    close(s); return 0;
}}
""".strip()
w("v4_get_tcp_repair_window.c", RW_GET_TPL.format(common=COMMON, sock="s4"))
w("v6_get_tcp_repair_window.c", RW_GET_TPL.format(common=COMMON, sock="s6"))
w("v4_set_tcp_repair_window.c", RW_SET_TPL.format(common=COMMON, sock="s4"))
w("v6_set_tcp_repair_window.c", RW_SET_TPL.format(common=COMMON, sock="s6"))

w("v4_set_tcp_fastopen_key.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    unsigned char key[TCP_FASTOPEN_KEY_LENGTH]={0};
    (void)setsockopt(s, IPPROTO_TCP, TCP_FASTOPEN_KEY, key, sizeof(key));
    close(s); return 0;
}
""")
w("v6_set_tcp_fastopen_key.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    unsigned char key[TCP_FASTOPEN_KEY_LENGTH]={0};
    (void)setsockopt(s, IPPROTO_TCP, TCP_FASTOPEN_KEY, key, sizeof(key));
    close(s); return 0;
}
""")

TLS_TPL = r"""
{common}
int main(void){{
    int s={sock}(); if(s<0) return 0;
    struct tls12_crypto_info_aes_gcm_128 ci; memset(&ci,0,sizeof(ci));
    ci.info.version = 0x0303; /* TLS_1_2_VERSION */
    ci.info.cipher_type = 51; /* TLS_CIPHER_AES_GCM_128 */
    (void)setsockopt(s, IPPROTO_TCP, {which}, &ci, sizeof(ci));
    close(s); return 0;
}}
""".strip()
w("v4_set_tls_tx.c", TLS_TPL.format(common=COMMON, sock="s4", which="TLS_TX"))
w("v6_set_tls_tx.c", TLS_TPL.format(common=COMMON, sock="s6", which="TLS_TX"))
w("v4_set_tls_rx.c", TLS_TPL.format(common=COMMON, sock="s4", which="TLS_RX"))
w("v6_set_tls_rx.c", TLS_TPL.format(common=COMMON, sock="s6", which="TLS_RX"))

IOCTL_TPL = r"""
{common}
int main(void){{
    int s={sock}(); if(s<0) return 0;
    int v=0;
    (void)ioctl(s, {cmd}, &v);
    close(s); return 0;
}}
""".strip()
ioctls = [("v4_ioctl_siocinq.c","s4","SIOCINQ"),
          ("v6_ioctl_siocinq.c","s6","SIOCINQ"),
          ("v4_ioctl_siocatmark.c","s4","SIOCATMARK"),
          ("v6_ioctl_siocatmark.c","s6","SIOCATMARK"),
          ("v4_ioctl_siocoutq.c","s4","SIOCOUTQ"),
          ("v6_ioctl_siocoutq.c","s6","SIOCOUTQ"),
          ("v4_ioctl_siocoutqnsd.c","s4","SIOCOUTQNSD"),
          ("v6_ioctl_siocoutqnsd.c","s6","SIOCOUTQNSD")]
for fname, sock, cmd in ioctls:
    w(fname, IOCTL_TPL.format(common=COMMON, sock=sock, cmd=cmd))
