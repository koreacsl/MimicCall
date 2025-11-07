import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_inet6"
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
#include <linux/in6.h>
#include <linux/route.h>
#include <linux/ipv6_route.h>
#include <linux/mroute6.h>
#include <linux/netfilter_ipv6/ip6_tables.h>

#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 02000000
#endif
#ifndef SOCK_NONBLOCK
#define SOCK_NONBLOCK 00004000
#endif

static int s_any6(void){
    int s = socket(AF_INET6, SOCK_DGRAM|SOCK_CLOEXEC, 0);
    if (s < 0) return -1;
    return s;
}
static void nb(int s){
    int fl = fcntl(s, F_GETFL, 0);
    if (fl >= 0) fcntl(s, F_SETFL, fl | O_NONBLOCK);
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

w("inet6_socket.c", COMMON + "int main(void){int s=s_any6(); if(s>=0) close(s); return 0;}\n")

w("inet6_send_recv.c", COMMON + r"""
int main(void){
    int s = s_any6(); if (s<0) return 0; nb(s); bind_loop6(s);
    struct sockaddr_in6 dst; memset(&dst,0,sizeof(dst));
    dst.sin6_family = AF_INET6; dst.sin6_port = htons(9); dst.sin6_addr = in6addr_loopback;
    (void)sendto(s, "", 0, 0, (struct sockaddr*)&dst, sizeof(dst));
    (void)recvfrom(s, NULL, 0, MSG_DONTWAIT, NULL, 0);
    close(s); return 0;
}
""")

inet6_int_opts = [
    "IPV6_ADDRFORM","IPV6_2292PKTINFO","IPV6_2292HOPOPTS","IPV6_2292DSTOPTS","IPV6_2292RTHDR",
    "IPV6_CHECKSUM","IPV6_2292HOPLIMIT","IPV6_NEXTHOP","IPV6_AUTHHDR","IPV6_FLOWINFO",
    "IPV6_UNICAST_HOPS","IPV6_MULTICAST_IF","IPV6_MULTICAST_HOPS","IPV6_MULTICAST_LOOP",
    "IPV6_ROUTER_ALERT","IPV6_MTU_DISCOVER","IPV6_MTU","IPV6_RECVERR","IPV6_V6ONLY",
    "IPV6_FLOWINFO_SEND","IPV6_HDRINCL","IPV6_RECVPKTINFO","IPV6_RECVHOPLIMIT","IPV6_HOPLIMIT",
    "IPV6_RECVHOPOPTS","IPV6_RECVRTHDR","IPV6_RECVDSTOPTS","IPV6_RECVPATHMTU","IPV6_DONTFRAG",
    "IPV6_RECVTCLASS","IPV6_TCLASS","IP6T_SO_ORIGINAL_DST","IPV6_AUTOFLOWLABEL","IPV6_ADDR_PREFERENCES",
    "IPV6_MINHOPCOUNT","IPV6_RECVORIGDSTADDR","IPV6_TRANSPARENT","IPV6_UNICAST_IF","MRT6_INIT",
    "MRT6_DONE","MRT6_DEL_MIF","MRT6_VERSION","MRT6_ASSERT","MRT6_PIM","MRT6_TABLE","IPV6_FREEBIND"
]

SET_INT_TPL = r"""
{common}
int main(void){{
    int s=s_any6(); if(s<0) return 0;
    int v=0;
    (void)setsockopt(s, IPPROTO_IPV6, {opt}, &v, sizeof(v));
    close(s); return 0;
}}
""".strip()

GET_INT_TPL = r"""
{common}
int main(void){{
    int s=s_any6(); if(s<0) return 0;
    int v=0; socklen_t l=sizeof(v);
    (void)getsockopt(s, IPPROTO_IPV6, {opt}, &v, &l);
    close(s); return 0;
}}
""".strip()

for opt in inet6_int_opts:
    level = "IPPROTO_IPV6"
    if "MRT6_" in opt:
        level = "IPPROTO_ICMPV6"
    elif "IP6T_" in opt:
        level = "IPPROTO_RAW"

    current_set_tpl = SET_INT_TPL.replace("IPPROTO_IPV6", level)
    current_get_tpl = GET_INT_TPL.replace("IPPROTO_IPV6", level)
    
    base = opt.lower()
    w(f"set_{base}.c", current_set_tpl.format(common=COMMON, opt=opt))
    w(f"get_{base}.c", current_get_tpl.format(common=COMMON, opt=opt))

inet6_buf_opts = [
    "IPV6_2292PKTOPTIONS","IPV6_FLOWLABEL_MGR","IPV6_IPSEC_POLICY","IPV6_XFRM_POLICY",
    "MCAST_JOIN_GROUP","MCAST_LEAVE_GROUP","MCAST_MSFILTER","IPV6_PKTINFO","IPV6_PATHMTU",
    "IP6T_SO_GET_REVISION_MATCH","IP6T_SO_GET_REVISION_TARGET","MRT6_ADD_MIF","MRT6_ADD_MFC",
    "MRT6_DEL_MFC","MRT6_ADD_MFC_PROXY","MRT6_DEL_MFC_PROXY"
]

SET_BUF_TPL = r"""
{common}
int main(void){{
    int s=s_any6(); if(s<0) return 0;
    char buf[16]; memset(buf,0,sizeof(buf));
    (void)setsockopt(s, {level}, {opt}, buf, (socklen_t)sizeof(buf));
    close(s); return 0;
}}
""".strip()

GET_BUF_TPL = r"""
{common}
int main(void){{
    int s=s_any6(); if(s<0) return 0;
    char buf[32]; socklen_t l=sizeof(buf);
    (void)getsockopt(s, {level}, {opt}, buf, &l);
    close(s); return 0;
}}
""".strip()

for opt in inet6_buf_opts:
    level = "IPPROTO_IPV6"
    if "MRT6_" in opt:
        level = "IPPROTO_ICMPV6"
    elif "MCAST_" in opt:
        level = "IPPROTO_IPV6"
    elif "IP6T_" in opt:
        level = "IPPROTO_RAW"

    base = opt.lower()
    w(f"set_{base}.c", SET_BUF_TPL.format(common=COMMON, level=level, opt=opt))
    w(f"get_{base}.c", GET_BUF_TPL.format(common=COMMON, level=level, opt=opt))

w("set_ipv6_addrform_specific.c", COMMON + r"""
int main(void){
    int s=s_any6(); if(s<0) return 0;
    int v = AF_INET;
    (void)setsockopt(s, IPPROTO_IPV6, IPV6_ADDRFORM, &v, sizeof(v));
    close(s); return 0;
}
""")

w("set_ipv6_flowlabel_mgr.c", COMMON + r"""
int main(void){
    int s=s_any6(); if(s<0) return 0;
    struct in6_flowlabel_req req; memset(&req,0,sizeof(req));
    (void)setsockopt(s, IPPROTO_IPV6, IPV6_FLOWLABEL_MGR, &req, sizeof(req));
    close(s); return 0;
}
""")

w("set_ipv6_pktinfo.c", COMMON + r"""
int main(void){
    int s=s_any6(); if(s<0) return 0;
    struct in6_pktinfo pi; memset(&pi,0,sizeof(pi));
    (void)setsockopt(s, IPPROTO_IPV6, IPV6_PKTINFO, &pi, sizeof(pi));
    close(s); return 0;
}
""")

w("set_ipv6_add_membership.c", COMMON + r"""
int main(void){
    int s=s_any6(); if(s<0) return 0;
    struct ipv6_mreq mr; memset(&mr,0,sizeof(mr));
    (void)setsockopt(s, IPPROTO_IPV6, IPV6_ADD_MEMBERSHIP, &mr, sizeof(mr));
    close(s); return 0;
}
""")
w("set_ipv6_drop_membership.c", COMMON + r"""
int main(void){
    int s=s_any6(); if(s<0) return 0;
    struct ipv6_mreq mr; memset(&mr,0,sizeof(mr));
    (void)setsockopt(s, IPPROTO_IPV6, IPV6_DROP_MEMBERSHIP, &mr, sizeof(mr));
    close(s); return 0;
}
""")

w("set_mcast_join_group.c", COMMON + r"""
#include <net/if.h>
int main(void){
    int s=s_any6(); if(s<0) return 0;
    struct group_req gr; memset(&gr,0,sizeof(gr));
    gr.gr_interface = 1; /* loopback */
    (void)setsockopt(s, IPPROTO_IPV6, MCAST_JOIN_GROUP, &gr, sizeof(gr));
    close(s); return 0;
}
""")
w("set_mcast_leave_group.c", COMMON + r"""
#include <net/if.h>
int main(void){
    int s=s_any6(); if(s<0) return 0;
    struct group_req gr; memset(&gr,0,sizeof(gr));
    gr.gr_interface = 1; /* loopback */
    (void)setsockopt(s, IPPROTO_IPV6, MCAST_LEAVE_GROUP, &gr, sizeof(gr));
    close(s); return 0;
}
""")

w("set_mcast_join_source_group.c", COMMON + r"""
#include <net/if.h>
int main(void){
    int s=s_any6(); if(s<0) return 0;
    struct group_source_req gsr; memset(&gsr,0,sizeof(gsr));
    gsr.gsr_interface = 1;
    (void)setsockopt(s, IPPROTO_IPV6, MCAST_JOIN_SOURCE_GROUP, &gsr, sizeof(gsr));
    close(s); return 0;
}
""")

w("set_ipv6_hopopts.c", COMMON + r"""
int main(void){
    int s=s_any6(); if(s<0) return 0;
    char buf[8]; memset(buf,0,sizeof(buf));
    (void)setsockopt(s, IPPROTO_IPV6, IPV6_HOPOPTS, buf, sizeof(buf));
    close(s); return 0;
}
""")
w("set_ipv6_rthdr.c", COMMON + r"""
int main(void){
    int s=s_any6(); if(s<0) return 0;
    char buf[8]; memset(buf,0,sizeof(buf));
    (void)setsockopt(s, IPPROTO_IPV6, IPV6_RTHDR, buf, sizeof(buf));
    close(s); return 0;
}
""")
w("set_ipv6_dstopts.c", COMMON + r"""
int main(void){
    int s=s_any6(); if(s<0) return 0;
    char buf[8]; memset(buf,0,sizeof(buf));
    (void)setsockopt(s, IPPROTO_IPV6, IPV6_DSTOPTS, buf, sizeof(buf));
    close(s); return 0;
}
""")

w("set_ipv6_mtu_discover.c", COMMON + r"""
int main(void){
    int s=s_any6(); if(s<0) return 0;
    int v = IPV6_PMTUDISC_DONT;
    (void)setsockopt(s, IPPROTO_IPV6, IPV6_MTU_DISCOVER, &v, sizeof(v));
    close(s); return 0;
}
""")

w("inet6_sendmsg_cmsg_tclass.c", COMMON + r"""
int main(void){
    int s=s_any6(); if(s<0) return 0; nb(s); bind_loop6(s);
    char buf[1]; struct iovec iov = { .iov_base = buf, .iov_len = 0 };
    char cbuf[CMSG_SPACE(sizeof(int))]; memset(cbuf,0,sizeof(cbuf));
    struct msghdr msg; memset(&msg,0,sizeof(msg));
    struct sockaddr_in6 dst; memset(&dst,0,sizeof(dst));
    dst.sin6_family = AF_INET6; dst.sin6_port = htons(9); dst.sin6_addr = in6addr_loopback;
    msg.msg_name = &dst; msg.msg_namelen = sizeof(dst);
    msg.msg_iov = &iov; msg.msg_iovlen = 1;
    msg.msg_control = cbuf; msg.msg_controllen = sizeof(cbuf);
    struct cmsghdr* c = CMSG_FIRSTHDR(&msg);
    if (c) {
        c->cmsg_level = IPPROTO_IPV6; c->cmsg_type = IPV6_TCLASS; c->cmsg_len = CMSG_LEN(sizeof(int));
        int t = 0; memcpy(CMSG_DATA(c), &t, sizeof(t));
    }
    (void)sendmsg(s, &msg, 0);
    close(s); return 0;
}
""")

w("ioctl_inet6_siocaddrt.c", COMMON + r"""
int main(void){
    int s=s_any6(); if(s<0) return 0;
    struct in6_rtmsg rt; memset(&rt,0,sizeof(rt));
    (void)ioctl(s, SIOCADDRT, &rt);
    close(s); return 0;
}
""")
w("ioctl_inet6_siocdelrt.c", COMMON + r"""
int main(void){
    int s=s_any6(); if(s<0) return 0;
    struct in6_rtmsg rt; memset(&rt,0,sizeof(rt));
    (void)ioctl(s, SIOCDELRT, &rt);
    close(s); return 0;
}
""")
w("ioctl_inet6_siocsifaddr.c", COMMON + r"""
#include <net/if.h>
int main(void){
    int s=s_any6(); if(s<0) return 0;
    struct in6_ifreq ifr; memset(&ifr,0,sizeof(ifr));
    ifr.ifr6_ifindex = 1; /* loopback */
    (void)ioctl(s, SIOCSIFADDR, &ifr);
    close(s); return 0;
}
""")
w("ioctl_inet6_siocdifaddr.c", COMMON + r"""
#include <net/if.h>
int main(void){
    int s=s_any6(); if(s<0) return 0;
    struct in6_ifreq ifr; memset(&ifr,0,sizeof(ifr));
    ifr.ifr6_ifindex = 1;
    (void)ioctl(s, SIOCDIFADDR, &ifr);
    close(s); return 0;
}
""")
w("ioctl_inet6_siocsifdstaddr.c", COMMON + r"""
#include <net/if.h>
int main(void){
    int s=s_any6(); if(s<0) return 0;
    struct in6_ifreq ifr; memset(&ifr,0,sizeof(ifr));
    ifr.ifr6_ifindex = 1;
    (void)ioctl(s, SIOCSIFDSTADDR, &ifr);
    close(s); return 0;
}
""")
