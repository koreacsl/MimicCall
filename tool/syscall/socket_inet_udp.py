import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_inet_udp"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/uio.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <linux/udp.h>
#include <linux/sockios.h>

#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 02000000
#endif
#ifndef SOCK_NONBLOCK
#define SOCK_NONBLOCK 00004000
#endif
#ifndef IPPROTO_UDP
#define IPPROTO_UDP 17
#endif
#ifndef IPPROTO_UDPLITE
#define IPPROTO_UDPLITE 136
#endif

static int s_udp4(void){
    int s = socket(AF_INET, SOCK_DGRAM|SOCK_CLOEXEC, IPPROTO_UDP);
    if (s < 0) return -1;
    return s;
}
static int s_udp6(void){
    int s = socket(AF_INET6, SOCK_DGRAM|SOCK_CLOEXEC, IPPROTO_UDP);
    if (s < 0) return -1;
    return s;
}
static int s_udplite4(void){
    int s = socket(AF_INET, SOCK_DGRAM|SOCK_CLOEXEC, IPPROTO_UDPLITE);
    if (s < 0) return -1;
    return s;
}
static int s_udplite6(void){
    int s = socket(AF_INET6, SOCK_DGRAM|SOCK_CLOEXEC, IPPROTO_UDPLITE);
    if (s < 0) return -1;
    return s;
}
static void nb(int s){
    int fl = fcntl(s, F_GETFL, 0);
    if (fl >= 0) fcntl(s, F_SETFL, fl | O_NONBLOCK);
}
static void bind_loop4(int s){
    struct sockaddr_in a; memset(&a,0,sizeof(a));
    a.sin_family = AF_INET; a.sin_port = 0; a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    (void)bind(s, (struct sockaddr*)&a, sizeof(a));
}
static void bind_loop6(int s){
    struct sockaddr_in6 a; memset(&a,0,sizeof(a));
    a.sin6_family = AF_INET6; a.sin6_port = 0; a.sin6_addr = in6addr_loopback;
    (void)bind(s, (struct sockaddr*)&a, sizeof(a));
}
""").lstrip()

def w(name, src):
    with open(os.path.join(OUTDIR, name), "w") as f:
        f.write(src)

w("udp_socket_v4.c", COMMON + "int main(void){int s=s_udp4(); if(s>=0) close(s); return 0;}\n")
w("udp_socket_v6.c", COMMON + "int main(void){int s=s_udp6(); if(s>=0) close(s); return 0;}\n")
w("udplite_socket_v4.c", COMMON + "int main(void){int s=s_udplite4(); if(s>=0) close(s); return 0;}\n")
w("udplite_socket_v6.c", COMMON + "int main(void){int s=s_udplite6(); if(s>=0) close(s); return 0;}\n")

w("udp_send_recv_v4.c", COMMON + r"""
int main(void){
    int s = s_udp4(); if (s<0) return 0; nb(s); bind_loop4(s);
    struct sockaddr_in dst; memset(&dst,0,sizeof(dst));
    dst.sin_family = AF_INET; dst.sin_port = htons(9); dst.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    (void)sendto(s, "", 0, 0, (struct sockaddr*)&dst, sizeof(dst));
    (void)recvfrom(s, NULL, 0, MSG_DONTWAIT, NULL, 0);
    close(s); return 0;
}
""")
w("udp_send_recv_v6.c", COMMON + r"""
int main(void){
    int s = s_udp6(); if (s<0) return 0; nb(s); bind_loop6(s);
    struct sockaddr_in6 dst; memset(&dst,0,sizeof(dst));
    dst.sin6_family = AF_INET6; dst.sin6_port = htons(9); dst.sin6_addr = in6addr_loopback;
    (void)sendto(s, "", 0, 0, (struct sockaddr*)&dst, sizeof(dst));
    (void)recvfrom(s, NULL, 0, MSG_DONTWAIT, NULL, 0);
    close(s); return 0;
}
""")

udp_int_opts = [
    "UDP_CORK", "UDP_NO_CHECK6_TX", "UDP_NO_CHECK6_RX", "UDP_SEGMENT",
    "UDPLITE_SEND_CSCOV", "UDPLITE_RECV_CSCOV"
]

SET_INT_TPL_V4 = r"""
{common}
int main(void){{
    int s=s_udp4(); if(s<0) return 0;
    int v=0;
    (void)setsockopt(s, IPPROTO_UDP, {opt}, &v, sizeof(v));
    close(s); return 0;
}}
""".strip()

GET_INT_TPL_V4 = r"""
{common}
int main(void){{
    int s=s_udp4(); if(s<0) return 0;
    int v=0; socklen_t l=sizeof(v);
    (void)getsockopt(s, IPPROTO_UDP, {opt}, &v, &l);
    close(s); return 0;
}}
""".strip()

SET_INT_TPL_V6 = r"""
{common}
int main(void){{
    int s=s_udp6(); if(s<0) return 0;
    int v=0;
    (void)setsockopt(s, IPPROTO_UDP, {opt}, &v, sizeof(v));
    close(s); return 0;
}}
""".strip()

GET_INT_TPL_V6 = r"""
{common}
int main(void){{
    int s=s_udp6(); if(s<0) return 0;
    int v=0; socklen_t l=sizeof(v);
    (void)getsockopt(s, IPPROTO_UDP, {opt}, &v, &l);
    close(s); return 0;
}}
""".strip()

for opt in udp_int_opts:
    proto = "IPPROTO_UDPLITE" if "UDPLITE" in opt else "IPPROTO_UDP"
    sock_v4 = "s_udplite4" if "UDPLITE" in opt else "s_udp4"
    sock_v6 = "s_udplite6" if "UDPLITE" in opt else "s_udp6"
    base = opt.lower()
    
    w(f"set_{base}_v4.c", SET_INT_TPL_V4.replace("{opt}", opt).replace("s_udp4", sock_v4).replace("IPPROTO_UDP", proto))
    w(f"get_{base}_v4.c", GET_INT_TPL_V4.replace("{opt}", opt).replace("s_udp4", sock_v4).replace("IPPROTO_UDP", proto))
    w(f"set_{base}_v6.c", SET_INT_TPL_V6.replace("{opt}", opt).replace("s_udp6", sock_v6).replace("IPPROTO_UDP", proto))
    w(f"get_{base}_v6.c", GET_INT_TPL_V6.replace("{opt}", opt).replace("s_udp6", sock_v6).replace("IPPROTO_UDP", proto))

encap_vals = [
    ("UDP_ENCAP_ESPINUDP_NON_IKE", "espnonike"),
    ("UDP_ENCAP_ESPINUDP",         "esp"),
    ("UDP_ENCAP_L2TPINUDP",        "l2tp"),
    ("UDP_ENCAP_GTP0",             "gtp0"),
    ("UDP_ENCAP_GTP1U",            "gtp1u"),
]

SET_ENCAP_V4 = r"""
{common}
int main(void){{
    int s=s_udp4(); if(s<0) return 0;
    int v = {val};
    (void)setsockopt(s, IPPROTO_UDP, UDP_ENCAP, &v, sizeof(v));
    close(s); return 0;
}}
""".strip()

SET_ENCAP_V6 = r"""
{common}
int main(void){{
    int s=s_udp6(); if(s<0) return 0;
    int v = {val};
    (void)setsockopt(s, IPPROTO_UDP, UDP_ENCAP, &v, sizeof(v));
    close(s); return 0;
}}
""".strip()

for val, tag in encap_vals:
    w(f"set_udp_encap_{tag}_v4.c", SET_ENCAP_V4.format(common=COMMON, val=val))
    w(f"set_udp_encap_{tag}_v6.c", SET_ENCAP_V6.format(common=COMMON, val=val))

w("ioctl_udp_siocinq_v4.c", COMMON + r"""
int main(void){
    int s=s_udp4(); if(s<0) return 0; int v=0;
    (void)ioctl(s, SIOCINQ, &v);
    close(s); return 0;
}
""")
w("ioctl_udp_siocinq_v6.c", COMMON + r"""
int main(void){
    int s=s_udp6(); if(s<0) return 0; int v=0;
    (void)ioctl(s, SIOCINQ, &v);
    close(s); return 0;
}
""")
w("ioctl_udp_siocoutq_v4.c", COMMON + r"""
int main(void){
    int s=s_udp4(); if(s<0) return 0; int v=0;
    (void)ioctl(s, SIOCOUTQ, &v);
    close(s); return 0;
}
""")
w("ioctl_udp_siocoutq_v6.c", COMMON + r"""
int main(void){
    int s=s_udp6(); if(s<0) return 0; int v=0;
    (void)ioctl(s, SIOCOUTQ, &v);
    close(s); return 0;
}
""")

w("udplite_send_recv_v4.c", COMMON + r"""
int main(void){
    int s = s_udplite4(); if (s<0) return 0; nb(s); bind_loop4(s);
    (void)sendto(s, "", 0, 0, NULL, 0);
    (void)recvfrom(s, NULL, 0, MSG_DONTWAIT, NULL, 0);
    close(s); return 0;
}
""")
w("udplite_send_recv_v6.c", COMMON + r"""
int main(void){
    int s = s_udplite6(); if (s<0) return 0; nb(s); bind_loop6(s);
    (void)sendto(s, "", 0, 0, NULL, 0);
    (void)recvfrom(s, NULL, 0, MSG_DONTWAIT, NULL, 0);
    close(s); return 0;
}
""")