import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_inet_l2tp"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <linux/net.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>
#include <linux/l2tp.h>

#ifndef IPPROTO_L2TP
#define IPPROTO_L2TP 115
#endif
#ifndef SOL_NETLINK
#define SOL_NETLINK 270
#endif
#ifndef NETLINK_GENERIC
#define NETLINK_GENERIC 16
#endif

static int s4(void){ int s=socket(AF_INET,  SOCK_DGRAM, IPPROTO_L2TP); if(s<0) return -1; return s; }
static int s6(void){ int s=socket(AF_INET6, SOCK_DGRAM, IPPROTO_L2TP); if(s<0) return -1; return s; }

static void sa4(struct sockaddr_l2tpip* sa){
    memset(sa,0,sizeof(*sa));
    sa->l2tp_family = AF_INET;
    sa->l2tp_conn_id = 0;
}
static void sa6(struct sockaddr_l2tpip6* sa){
    memset(sa,0,sizeof(*sa));
    sa->l2tp_family = AF_INET6;
    sa->l2tp_conn_id = 0;
}

static int s_nl(void){
    struct sockaddr_nl nl = {0};
    int s = socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
    if (s < 0) return -1;
    nl.nl_family = AF_NETLINK;
    (void)bind(s, (struct sockaddr*)&nl, sizeof(nl));
    return s;
}
static void nl_send_cmd(uint8_t genl_cmd){
    int s = s_nl(); if (s < 0) return;
    char buf[128]; memset(buf, 0, sizeof(buf));
    struct nlmsghdr* nlh = (struct nlmsghdr*)buf;
    struct genlmsghdr* gh = (struct genlmsghdr*)(buf + NLMSG_HDRLEN);
    nlh->nlmsg_len = NLMSG_HDRLEN + GENL_HDRLEN;
    nlh->nlmsg_type = 0; /* family id unknown; still exercises sendmsg */
    nlh->nlmsg_flags = 0;
    gh->cmd = genl_cmd;
    struct sockaddr_nl dst = {0}; dst.nl_family = AF_NETLINK;
    struct iovec iov = { nlh, nlh->nlmsg_len };
    struct msghdr msg = {0};
    msg.msg_name = &dst; msg.msg_namelen = sizeof(dst);
    msg.msg_iov = &iov; msg.msg_iovlen = 1;
    (void)sendmsg(s, &msg, 0);
    close(s);
}
static void nl_send_attr_u16(uint16_t attr_type, uint16_t val){
    int s = s_nl(); if (s < 0) return;
    char buf[128]; memset(buf,0,sizeof(buf));
    struct nlmsghdr* nlh = (struct nlmsghdr*)buf;
    struct genlmsghdr* gh = (struct genlmsghdr*)(buf + NLMSG_HDRLEN);
    size_t off = NLMSG_HDRLEN + GENL_HDRLEN;
    struct nlattr* na = (struct nlattr*)(buf + off);
    na->nla_len = NLA_HDRLEN + sizeof(uint16_t);
    na->nla_type = attr_type;
    memcpy(NLA_DATA(na), &val, sizeof(uint16_t));
    nlh->nlmsg_len = off + na->nla_len;
    nlh->nlmsg_type = 0;
    nlh->nlmsg_flags = 0;
    gh->cmd = 0; /* any */
    struct sockaddr_nl dst = {0}; dst.nl_family = AF_NETLINK;
    struct iovec iov = { nlh, nlh->nlmsg_len };
    struct msghdr msg = {0};
    msg.msg_name = &dst; msg.msg_namelen = sizeof(dst);
    msg.msg_iov = &iov; msg.msg_iovlen = 1;
    (void)sendmsg(s, &msg, 0);
    close(s);
}
""").lstrip()

def w(name, src):
    with open(os.path.join(OUTDIR, name), "w") as f:
        f.write(src)

w("socket_v4.c", COMMON + r"""
int main(void){ int s=s4(); if(s>=0) close(s); return 0; }
""")
w("socket_v6.c", COMMON + r"""
int main(void){ int s=s6(); if(s>=0) close(s); return 0; }
""")

w("bind_v4.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    struct sockaddr_l2tpip sa; sa4(&sa);
    (void)bind(s,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}
""")
w("connect_v4.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    struct sockaddr_l2tpip sa; sa4(&sa);
    (void)connect(s,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}
""")
w("sendto_v4.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    struct sockaddr_l2tpip sa; sa4(&sa);
    char b=0;
    (void)sendto(s,&b,1,0,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}
""")
w("recvfrom_v4.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    (void)recvfrom(s,NULL,0,0,NULL,0);
    close(s); return 0;
}
""")
w("getsockname_v4.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    struct sockaddr_l2tpip sa; socklen_t l=sizeof(sa);
    (void)getsockname(s,(struct sockaddr*)&sa,&l);
    close(s); return 0;
}
""")
w("getpeername_v4.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    struct sockaddr_l2tpip sa; socklen_t l=sizeof(sa);
    (void)getpeername(s,(struct sockaddr*)&sa,&l);
    close(s); return 0;
}
""")

w("bind_v6.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    struct sockaddr_l2tpip6 sa; sa6(&sa);
    (void)bind(s,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}
""")
w("connect_v6.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    struct sockaddr_l2tpip6 sa; sa6(&sa);
    (void)connect(s,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}
""")
w("sendto_v6.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    struct sockaddr_l2tpip6 sa; sa6(&sa);
    char b=0;
    (void)sendto(s,&b,1,0,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}
""")
w("recvfrom_v6.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    (void)recvfrom(s,NULL,0,0,NULL,0);
    close(s); return 0;
}
""")
w("getsockname_v6.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    struct sockaddr_l2tpip6 sa; socklen_t l=sizeof(sa);
    (void)getsockname(s,(struct sockaddr*)&sa,&l);
    close(s); return 0;
}
""")
w("getpeername_v6.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    struct sockaddr_l2tpip6 sa; socklen_t l=sizeof(sa);
    (void)getpeername(s,(struct sockaddr*)&sa,&l);
    close(s); return 0;
}
""")

cmds = [
    ("l2tp_cmd_noop.c",           "L2TP_CMD_NOOP"),
    ("l2tp_cmd_tunnel_create.c",  "L2TP_CMD_TUNNEL_CREATE"),
    ("l2tp_cmd_tunnel_delete.c",  "L2TP_CMD_TUNNEL_DELETE"),
    ("l2tp_cmd_tunnel_modify.c",  "L2TP_CMD_TUNNEL_MODIFY"),
    ("l2tp_cmd_tunnel_get.c",     "L2TP_CMD_TUNNEL_GET"),
    ("l2tp_cmd_session_create.c", "L2TP_CMD_SESSION_CREATE"),
    ("l2tp_cmd_session_delete.c", "L2TP_CMD_SESSION_DELETE"),
    ("l2tp_cmd_session_modify.c", "L2TP_CMD_SESSION_MODIFY"),
    ("l2tp_cmd_session_get.c",    "L2TP_CMD_SESSION_GET"),
]
for fname, cmd in cmds:
    w(fname, COMMON + f"""
int main(void){{ nl_send_cmd({cmd}); return 0; }}
""")

pwtypes = ["L2TP_PWTYPE_NONE","L2TP_PWTYPE_ETH_VLAN","L2TP_PWTYPE_ETH","L2TP_PWTYPE_PPP","L2TP_PWTYPE_PPP_AC","L2TP_PWTYPE_IP"]
for p in pwtypes:
    tag = p.lower().replace("l2tp_pwtype_","")
    w(f"nlattr_pwtype_{tag}.c", COMMON + f"""
int main(void){{ nl_send_attr_u16(L2TP_ATTR_PW_TYPE, (uint16_t){p}); return 0; }}
""")

l2spec = ["L2TP_L2SPECTYPE_NONE","L2TP_L2SPECTYPE_DEFAULT"]
for v in l2spec:
    tag = v.lower().replace("l2tp_l2spectype_","")
    w(f"nlattr_l2spec_{tag}.c", COMMON + f"""
int main(void){{ nl_send_attr_u16(L2TP_ATTR_L2SPEC_TYPE, (uint16_t){v}); return 0; }}
""")

encaps = ["L2TP_ENCAPTYPE_UDP","L2TP_ENCAPTYPE_IP"]
for v in encaps:
    tag = v.lower().replace("l2tp_encaptype_","")
    w(f"nlattr_encap_{tag}.c", COMMON + f"""
int main(void){{ nl_send_attr_u16(L2TP_ATTR_ENCAP_TYPE, (uint16_t){v}); return 0; }}
""")
