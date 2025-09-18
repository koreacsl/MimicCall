import os
from textwrap import dedent

OUT = "./tool/cfiles/socket_netlink"
os.makedirs(OUT, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/net.h>

#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 02000000
#endif

static int nl_open(int proto){
    int s = socket(AF_NETLINK, SOCK_RAW|SOCK_CLOEXEC, proto);
    if (s >= 0){
        int f = fcntl(s, F_GETFL, 0);
        if (f >= 0) (void)fcntl(s, F_SETFL, f|O_NONBLOCK);
    }
    return s;
}

static void nl_bind_self(int s){
    struct sockaddr_nl a; memset(&a,0,sizeof(a));
    a.nl_family = AF_NETLINK;
    a.nl_pid = (uint32_t)getpid();
    (void)bind(s,(struct sockaddr*)&a,sizeof(a));
}

static void nl_connect_kern(int s){
    struct sockaddr_nl a; memset(&a,0,sizeof(a));
    a.nl_family = AF_NETLINK;
    a.nl_pid = 0;
    (void)connect(s,(struct sockaddr*)&a,sizeof(a));
}

static void nl_names(int s){
    struct sockaddr_nl a; socklen_t l=sizeof(a);
    (void)getsockname(s,(struct sockaddr*)&a,&l);
    (void)getpeername(s,(struct sockaddr*)&a,&l);
}

static void nl_send_noop(int s){
    char buf[64]; memset(buf,0,sizeof(buf));
    struct nlmsghdr *nh=(struct nlmsghdr*)buf;
    nh->nlmsg_len = NLMSG_LENGTH(0);
    nh->nlmsg_type = NLMSG_NOOP;
    nh->nlmsg_flags = 0;
    nh->nlmsg_seq = 1;
    nh->nlmsg_pid = (uint32_t)getpid();
    struct sockaddr_nl nl; memset(&nl,0,sizeof(nl));
    nl.nl_family = AF_NETLINK;
    struct iovec iov = {.iov_base=nh,.iov_len=nh->nlmsg_len};
    struct msghdr msg; memset(&msg,0,sizeof(msg));
    msg.msg_name=&nl; msg.msg_namelen=sizeof(nl);
    msg.msg_iov=&iov; msg.msg_iovlen=1;
    (void)sendmsg(s,&msg,0);
}

static void nl_try_setsockopt_int(int s, int opt, int val){
    (void)setsockopt(s, SOL_NETLINK, opt, &val, sizeof(val));
}
""").lstrip()

def w(name: str, body: str):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(body)

w("nl_basic_generic.c", COMMON + r"""
int main(void){
    int s = nl_open(NETLINK_GENERIC);
    if (s < 0) return 0;
    nl_bind_self(s);
    nl_connect_kern(s);
    nl_names(s);
    nl_send_noop(s);
    close(s);
    return 0;
}
""")

protos = [
    ("route", "NETLINK_ROUTE"),
    ("usersock", "NETLINK_USERSOCK"),
    ("sock_diag", "NETLINK_SOCK_DIAG"),
    ("xfrm", "NETLINK_XFRM"),
    ("selinux", "NETLINK_SELINUX"),
    ("audit", "NETLINK_AUDIT"),
    ("connector", "NETLINK_CONNECTOR"),
    ("netfilter", "NETLINK_NETFILTER"),
    ("kobject_uevent", "NETLINK_KOBJECT_UEVENT"),
    ("generic", "NETLINK_GENERIC"),
    ("rdma", "NETLINK_RDMA"),
    ("crypto", "NETLINK_CRYPTO"),
    ("inet_diag", "NETLINK_INET_DIAG"),
]
for suf, sym in protos:
    w(f"nl_basic_{suf}.c", COMMON + f"""
int main(void){{
    int s = nl_open({sym});
    if (s < 0) return 0;
    nl_bind_self(s);
    nl_connect_kern(s);
    nl_send_noop(s);
    close(s);
    return 0;
}}
""")

w("nl_membership.c", COMMON + r"""
static void add_drop(int s, int grp){
    (void)setsockopt(s, SOL_NETLINK, NETLINK_ADD_MEMBERSHIP, &grp, sizeof(grp));
    (void)setsockopt(s, SOL_NETLINK, NETLINK_DROP_MEMBERSHIP, &grp, sizeof(grp));
}
int main(void){
    int s = nl_open(NETLINK_GENERIC);
    if (s < 0) return 0;
    nl_bind_self(s);
    int groups[] = {0,1,2};
    for (unsigned i=0;i<sizeof(groups)/sizeof(groups[0]);++i) add_drop(s, groups[i]);
    close(s);
    return 0;
}
""")

w("nl_setsockopt_ints.c", COMMON + r"""
int main(void){
    int s = nl_open(NETLINK_GENERIC);
    if (s < 0) return 0;
    int opts[] = { NETLINK_PKTINFO, NETLINK_BROADCAST_ERROR, NETLINK_NO_ENOBUFS, NETLINK_LISTEN_ALL_NSID, NETLINK_CAP_ACK };
    for (unsigned i=0;i<sizeof(opts)/sizeof(opts[0]);++i){
        nl_try_setsockopt_int(s, opts[i], 1);
        nl_try_setsockopt_int(s, opts[i], 0);
    }
    close(s);
    return 0;
}
""")

w("nl_rings.c", COMMON + r"""
struct nl_mmap_req { uint32_t nm_block_size, nm_block_nr, nm_frame_size, nm_frame_nr; };
int main(void){
    int s = nl_open(NETLINK_GENERIC);
    if (s < 0) return 0;
    struct nl_mmap_req r; memset(&r,0,sizeof(r));
    (void)setsockopt(s, SOL_NETLINK, NETLINK_RX_RING, &r, sizeof(r));
    (void)setsockopt(s, SOL_NETLINK, NETLINK_TX_RING, &r, sizeof(r));
    close(s);
    return 0;
}
""")

w("nl_getsockopt.c", COMMON + r"""
int main(void){
    int s = nl_open(NETLINK_GENERIC);
    if (s < 0) return 0;
    int opts[] = { NETLINK_ADD_MEMBERSHIP, NETLINK_DROP_MEMBERSHIP, NETLINK_PKTINFO, NETLINK_BROADCAST_ERROR, NETLINK_NO_ENOBUFS, NETLINK_RX_RING, NETLINK_TX_RING, NETLINK_LISTEN_ALL_NSID, NETLINK_LIST_MEMBERSHIPS, NETLINK_CAP_ACK };
    for (unsigned i=0;i<sizeof(opts)/sizeof(opts[0]);++i){
        char buf[128]; socklen_t l=sizeof(buf);
        (void)getsockopt(s, SOL_NETLINK, opts[i], buf, &l);
    }
    close(s);
    return 0;
}
""")
