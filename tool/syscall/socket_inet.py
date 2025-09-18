import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_inet"
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

#include <linux/ip.h>
#include <linux/ipv6.h>
#include <linux/route.h>
#include <linux/if_arp.h>
#include <linux/in.h>


#ifndef IPPROTO_IP
#define IPPROTO_IP 0
#endif
#ifndef SOL_IP
#define SOL_IP IPPROTO_IP
#endif
#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 02000000
#endif
#ifndef SOCK_NONBLOCK
#define SOCK_NONBLOCK 00004000
#endif

static int s_dgram(void){
    int s = socket(AF_INET, SOCK_DGRAM|SOCK_CLOEXEC, 0);
    if (s < 0) return -1;
    return s;
}
static int s_stream(void){
    int s = socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, 0);
    if (s < 0) return -1;
    return s;
}
static void nb(int s){
    int fl = fcntl(s, F_GETFL, 0);
    if (fl >= 0) fcntl(s, F_SETFL, fl | O_NONBLOCK);
}
static void bind_any4(int s){
    struct sockaddr_in a;
    memset(&a, 0, sizeof(a));
    a.sin_family = AF_INET;
    a.sin_port = 0;
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    (void)bind(s, (struct sockaddr*)&a, sizeof(a));
}
""").lstrip()

def w(name, src):
    with open(os.path.join(OUTDIR, name), "w") as f:
        f.write(src)

w("socket_udp.c", COMMON + "int main(void){int s=s_dgram(); if(s>=0) close(s); return 0;}\n")
w("socket_tcp.c", COMMON + "int main(void){int s=s_stream(); if(s>=0) close(s); return 0;}\n")

w("inet_bind_connect_send_recv.c", COMMON + r"""
int main(void){
    int s = s_dgram(); if (s<0) return 0;
    bind_any4(s);

    struct sockaddr_in dst; memset(&dst,0,sizeof(dst));
    dst.sin_family = AF_INET;
    dst.sin_port = htons(9);
    dst.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    (void)connect(s, (struct sockaddr*)&dst, sizeof(dst));
    (void)sendto(s, "", 0, 0, (struct sockaddr*)&dst, sizeof(dst));
    (void)recvfrom(s, NULL, 0, MSG_DONTWAIT, NULL, 0);

    struct sockaddr_in n; socklen_t nl=sizeof(n);
    (void)getsockname(s, (struct sockaddr*)&n, &nl);

    struct sockaddr_in p; socklen_t pl=sizeof(p);
    (void)getpeername(s, (struct sockaddr*)&p, &pl);

    close(s); return 0;
}
""")

w("inet_accept.c", COMMON + r"""
int main(void){
    int l = s_stream(); if(l<0) return 0;
    nb(l);
    bind_any4(l);
    (void)listen(l, 1);
    (void)accept(l, NULL, NULL);
    (void)accept4(l, NULL, NULL, SOCK_NONBLOCK|SOCK_CLOEXEC);
    close(l); return 0;
}
""")

int_opts = [
 "IP_TOS","IP_TTL","IP_HDRINCL","IP_ROUTER_ALERT","IP_RECVOPTS","IP_RETOPTS",
 "IP_PKTINFO","IP_MTU_DISCOVER","IP_RECVERR","IP_RECVTTL","IP_RECVTOS","IP_MTU",
 "IP_FREEBIND","IP_PASSSEC","IP_TRANSPARENT","IP_RECVORIGDSTADDR","IP_MINTTL",
 "IP_NODEFRAG","IP_CHECKSUM","IP_BIND_ADDRESS_NO_PORT","IP_MULTICAST_TTL",
 "IP_MULTICAST_LOOP","IP_MULTICAST_ALL","IP_UNICAST_IF"
]

SET_INT_TPL = r"""
{common}
int main(void){{
    int s=s_dgram(); if(s<0) return 0;
    int v=0;
    (void)setsockopt(s, SOL_IP, {opt}, &v, sizeof(v));
    close(s); return 0;
}}
""".strip()

GET_INT_TPL = r"""
{common}
int main(void){{
    int s=s_dgram(); if(s<0) return 0;
    int v=0; socklen_t l=sizeof(v);
    (void)getsockopt(s, SOL_IP, {opt}, &v, &l);
    close(s); return 0;
}}
""".strip()

for opt in int_opts:
    base = opt.lower()
    w(f"set_{base}.c", SET_INT_TPL.format(common=COMMON, opt=opt))
    w(f"get_{base}.c", GET_INT_TPL.format(common=COMMON, opt=opt))

buf_opts = [
 "IP_OPTIONS","IP_PKTOPTIONS","IP_IPSEC_POLICY","IP_XFRM_POLICY",
 "IP_MSFILTER","MCAST_JOIN_GROUP","MCAST_LEAVE_SOURCE_GROUP","MCAST_MSFILTER"
]
SET_BUF_TPL = r"""
{common}
int main(void){{
    int s=s_dgram(); if(s<0) return 0;
    unsigned char b[4]={{0}};
    (void)setsockopt(s, SOL_IP, {opt}, b, sizeof(b));
    close(s); return 0;
}}
""".strip()
GET_BUF_TPL = r"""
{common}
int main(void){{
    int s=s_dgram(); if(s<0) return 0;
    unsigned char b[64]; socklen_t l=sizeof(b);
    (void)getsockopt(s, SOL_IP, {opt}, b, &l);
    close(s); return 0;
}}
""".strip()
for opt in buf_opts:
    base = opt.lower()
    w(f"set_{base}.c", SET_BUF_TPL.format(common=COMMON, opt=opt))
    w(f"get_{base}.c", GET_BUF_TPL.format(common=COMMON, opt=opt))

w("set_ip_add_membership.c", COMMON + r"""
int main(void){
    int s=s_dgram(); if(s<0) return 0;
    struct ip_mreq m; memset(&m,0,sizeof(m));
    m.imr_multiaddr.s_addr = htonl(0xE0000001u); /* 224.0.0.1 */
    (void)setsockopt(s, SOL_IP, IP_ADD_MEMBERSHIP, &m, sizeof(m));
    close(s); return 0;
}
""")
w("set_ip_drop_membership.c", COMMON + r"""
int main(void){
    int s=s_dgram(); if(s<0) return 0;
    struct ip_mreq m; memset(&m,0,sizeof(m));
    (void)setsockopt(s, SOL_IP, IP_DROP_MEMBERSHIP, &m, sizeof(m));
    close(s); return 0;
}
""")
w("set_ip_multicast_if_mreqn.c", COMMON + r"""
int main(void){
    int s=s_dgram(); if(s<0) return 0;
    struct ip_mreqn n; memset(&n,0,sizeof(n));
    (void)setsockopt(s, SOL_IP, IP_MULTICAST_IF, &n, sizeof(n));
    close(s); return 0;
}
""")
w("set_ip_add_source_membership.c", COMMON + r"""
int main(void){
    int s=s_dgram(); if(s<0) return 0;
    struct ip_mreq_source x; memset(&x,0,sizeof(x));
    (void)setsockopt(s, SOL_IP, IP_ADD_SOURCE_MEMBERSHIP, &x, sizeof(x));
    close(s); return 0;
}
""")

w("get_ip_pktinfo.c", COMMON + r"""
int main(void){
    int s=s_dgram(); if(s<0) return 0;
    struct in_pktinfo pi; socklen_t l=sizeof(pi);
    (void)getsockopt(s, SOL_IP, IP_PKTINFO, &pi, &l);
    close(s); return 0;
}
""")
w("set_ip_pktinfo.c", COMMON + r"""
int main(void){
    int s=s_dgram(); if(s<0) return 0;
    struct in_pktinfo pi; memset(&pi,0,sizeof(pi));
    (void)setsockopt(s, SOL_IP, IP_PKTINFO, &pi, sizeof(pi));
    close(s); return 0;
}
""")
w("get_ip_mtu_discover.c", COMMON + r"""
int main(void){
    int s=s_dgram(); if(s<0) return 0;
    int v=0; socklen_t l=sizeof(v);
    (void)getsockopt(s, SOL_IP, IP_MTU_DISCOVER, &v, &l);
    close(s); return 0;
}
""")
w("set_ip_mtu_discover.c", COMMON + r"""
int main(void){
    int s=s_dgram(); if(s<0) return 0;
    int v=IP_PMTUDISC_DONT;
    (void)setsockopt(s, SOL_IP, IP_MTU_DISCOVER, &v, sizeof(v));
    close(s); return 0;
}
""")

w("ioctl_route.c", COMMON + r"""
#include <net/route.h>
int main(void){
    int s=s_dgram(); if(s<0) return 0;
    struct rtentry rt; memset(&rt,0,sizeof(rt));
    (void)ioctl(s, SIOCADDRT, &rt);
    (void)ioctl(s, SIOCDELRT, &rt);
    /* SIOCRTMSG is not a standard ioctl command */
    close(s); return 0;
}
""")
w("ioctl_arp.c", COMMON + r"""
int main(void){
    int s=s_dgram(); if(s<0) return 0;
    struct arpreq ar; memset(&ar,0,sizeof(ar));
    (void)ioctl(s, SIOCDARP, &ar);
    (void)ioctl(s, SIOCGARP, &ar);
    (void)ioctl(s, SIOCSARP, &ar);
    close(s); return 0;
}
""")
w("ioctl_ifaddr.c", COMMON + r"""
#include <net/if.h>
int main(void){
    int s=s_dgram(); if(s<0) return 0;
    struct ifreq rq; memset(&rq,0,sizeof(rq));
    strncpy(rq.ifr_name, "lo", IFNAMSIZ-1);
    (void)ioctl(s, SIOCGIFADDR, &rq);
    (void)ioctl(s, SIOCSIFADDR, &rq);
    (void)ioctl(s, SIOCGIFBRDADDR, &rq);
    (void)ioctl(s, SIOCSIFBRDADDR, &rq);
    (void)ioctl(s, SIOCGIFNETMASK, &rq);
    (void)ioctl(s, SIOCSIFNETMASK, &rq);
    (void)ioctl(s, SIOCGIFDSTADDR, &rq);
    (void)ioctl(s, SIOCSIFDSTADDR, &rq);
    (void)ioctl(s, SIOCSIFFLAGS, &rq);
    close(s); return 0;
}
""")

w("inet_sendmsg.c", COMMON + r"""
int main(void){
    int s=s_dgram(); if(s<0) return 0;
    struct msghdr mh; memset(&mh,0,sizeof(mh));
    (void)sendmsg(s, &mh, 0);
    close(s); return 0;
}
""")
w("inet_sendmmsg.c", COMMON + r"""
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <sys/socket.h>
int main(void){
    int s=s_dgram(); if(s<0) return 0;
    struct mmsghdr mm; memset(&mm,0,sizeof(mm));
    (void)sendmmsg(s, &mm, 1, 0);
    close(s); return 0;
}
""")