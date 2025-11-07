import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_ip_tunnel"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <net/if.h>

/* Use standard uapi headers from the system */
#include <linux/if_tunnel.h>
#include <linux/ip6_tunnel.h>

#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 02000000
#endif

#ifndef ifr_data
# define ifr_data ifr_ifru.ifru_data
#endif

static int s4(void){
    int s = socket(AF_INET, SOCK_DGRAM|SOCK_CLOEXEC, 0);
    if (s >= 0) {
        int fl = fcntl(s, F_GETFL, 0);
        if (fl >= 0) fcntl(s, F_SETFL, fl | O_NONBLOCK);
    }
    return s;
}
static int s6(void){
    int s = socket(AF_INET6, SOCK_DGRAM|SOCK_CLOEXEC, 0);
    if (s >= 0) {
        int fl = fcntl(s, F_GETFL, 0);
        if (fl >= 0) fcntl(s, F_SETFL, fl | O_NONBLOCK);
    }
    return s;
}
""").lstrip()

def wr(name: str, src: str):
    with open(os.path.join(OUTDIR, name), "w") as f:
        f.write(src)

wr("ipv4_get_add_del_chg_tunnel.c", COMMON + r"""
int main(void){
    int s = s4(); if (s < 0) return 0;

    struct ip_tunnel_parm p; memset(&p, 0, sizeof(p));
    strncpy(p.name, "tunl0", sizeof(p.name)-1);
    p.link = 0;

    struct ifreq ifr; memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, "tunl0", sizeof(ifr.ifr_name)-1);
    ifr.ifr_data = (void*)&p;

    (void)ioctl(s, SIOCGETTUNNEL, &ifr);
    (void)ioctl(s, SIOCADDTUNNEL, &ifr);
    (void)ioctl(s, SIOCCHGTUNNEL, &ifr);
    (void)ioctl(s, SIOCDELTUNNEL, &ifr);

    close(s); return 0;
}
""")

wr("ipv6_get_add_del_chg_tunnel.c", COMMON + r"""
int main(void){
    int s = s6(); if (s < 0) return 0;

    struct ip6_tnl_parm2 p6; memset(&p6, 0, sizeof(p6));
    strncpy(p6.name, "ip6tnl0", sizeof(p6.name)-1);
    p6.link = 0;

    struct ifreq ifr; memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, "ip6tnl0", sizeof(ifr.ifr_name)-1);
    ifr.ifr_data = (void*)&p6;

    (void)ioctl(s, SIOCGETTUNNEL, &ifr);
    (void)ioctl(s, SIOCADDTUNNEL, &ifr);
    (void)ioctl(s, SIOCCHGTUNNEL, &ifr);
    (void)ioctl(s, SIOCDELTUNNEL, &ifr);

    close(s); return 0;
}
""")

ipv4_io_flags = [
    "GRE_CSUM","GRE_ROUTING","GRE_KEY","GRE_SEQ","GRE_STRICT","GRE_REC",
    "GRE_ACK","GRE_FLAGS","GRE_VERSION","VTI_ISVTI",
]
TPL_V4_FLAG = r"""
{common}
int main(void){{
    int s = s4(); if (s < 0) return 0;

    struct ip_tunnel_parm p; memset(&p, 0, sizeof(p));
    strncpy(p.name, "tunl0", sizeof(p.name)-1);
    p.i_flags = htons({flag});
    p.link = 0;

    struct ifreq ifr; memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, "tunl0", sizeof(ifr.ifr_name)-1);
    ifr.ifr_data = (void*)&p;

    (void)ioctl(s, SIOCCHGTUNNEL, &ifr);
    close(s); return 0;
}}
""".strip()

for fl in ipv4_io_flags:
    wr(f"ipv4_iflag_{fl.lower()}.c", TPL_V4_FLAG.format(common=COMMON, flag=fl))

ipv6_tnl_flags = [
    "IP6_TNL_F_IGN_ENCAP_LIMIT","IP6_TNL_F_USE_ORIG_TCLASS","IP6_TNL_F_USE_ORIG_FLOWLABEL",
    "IP6_TNL_F_MIP6_DEV","IP6_TNL_F_RCV_DSCP_COPY","IP6_TNL_F_USE_ORIG_FWMARK","IP6_TNL_F_ALLOW_LOCAL_REMOTE",
]

TPL_V6_FLAG = r"""
{common}
int main(void){{
    int s = s6(); if (s < 0) return 0;

    struct ip6_tnl_parm2 p6; memset(&p6, 0, sizeof(p6));
    strncpy(p6.name, "ip6tnl0", sizeof(p6.name)-1);
    p6.flags = {flag};

    struct ifreq ifr; memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, "ip6tnl0", sizeof(ifr.ifr_name)-1);
    ifr.ifr_data = (void*)&p6;

    (void)ioctl(s, SIOCCHGTUNNEL, &ifr);
    close(s); return 0;
}}
""".strip()

for fl in ipv6_tnl_flags:
    wr(f"ipv6_flag_{fl.lower().replace('ip6_tnl_f_', '')}.c", TPL_V6_FLAG.format(common=COMMON, flag=fl))

ip_tunnel_protocols = ["IPPROTO_IPIP", "IPPROTO_GRE", "IPPROTO_IPV6"]

TPL_V4_PROTO = r"""
{common}
int main(void){{
    int s = s4(); if (s < 0) return 0;

    struct ip_tunnel_parm p; memset(&p, 0, sizeof(p));
    strncpy(p.name, "tunl0", sizeof(p.name)-1);
    p.iph.version = 4;
    p.iph.ihl = 5;
    p.iph.protocol = {proto};

    struct ifreq ifr; memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, "tunl0", sizeof(ifr.ifr_name)-1);
    ifr.ifr_data = (void*)&p;

    (void)ioctl(s, SIOCCHGTUNNEL, &ifr);
    close(s); return 0;
}}
""".strip()

for proto in ip_tunnel_protocols:
    wr(f"ipv4_proto_{proto.lower()}.c", TPL_V4_PROTO.format(common=COMMON, proto=proto))

TPL_V6_PROTO = r"""
{common}
int main(void){{
    int s = s6(); if (s < 0) return 0;

    struct ip6_tnl_parm2 p6; memset(&p6, 0, sizeof(p6));
    strncpy(p6.name, "ip6tnl0", sizeof(p6.name)-1);
    p6.proto = {proto};

    struct ifreq ifr; memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, "ip6tnl0", sizeof(ifr.ifr_name)-1);
    ifr.ifr_data = (void*)&p6;

    (void)ioctl(s, SIOCCHGTUNNEL, &ifr);
    close(s); return 0;
}}
""".strip()

for proto in ip_tunnel_protocols:
    wr(f"ipv6_proto_{proto.lower()}.c", TPL_V6_PROTO.format(common=COMMON, proto=proto))

TPL_PRL = r"""
{common}
int main(void){{
    int s = s4(); if (s < 0) return 0;

    struct ip_tunnel_prl prl; memset(&prl, 0, sizeof(prl));
    prl.addr = htonl(INADDR_ANY);
    prl.flags = {flags};

    struct ifreq ifr; memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, "sit0", sizeof(ifr.ifr_name)-1);
    ifr.ifr_data = (void*)&prl;

    (void)ioctl(s, {cmd}, &ifr);
    close(s); return 0;
}}
""".strip()

prl_cmds = [
    ("SIOCGETPRL", "0"),
    ("SIOCADDPRL", "PRL_DEFAULT"),
    ("SIOCDELPRL", "PRL_DEFAULT"),
    ("SIOCCHGPRL", "PRL_DEFAULT"),
]
for cmd, fl in prl_cmds:
    wr(f"ipv4_prl_{cmd.lower()}.c", TPL_PRL.format(common=COMMON, cmd=cmd, flags=fl))

wr("ipv4_6rd_get.c", COMMON + r"""
int main(void){
    int s = s4(); if (s < 0) return 0;

    struct ip_tunnel_6rd p6rd; memset(&p6rd, 0, sizeof(p6rd));

    struct ifreq ifr; memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, "sit0", sizeof(ifr.ifr_name)-1);
    ifr.ifr_data = (void*)&p6rd;

    (void)ioctl(s, SIOCGET6RD, &ifr);
    close(s); return 0;
}
""")

TPL_6RD = r"""
{common}
int main(void){{
    int s = s4(); if (s < 0) return 0;

    struct ip_tunnel_6rd p6rd; memset(&p6rd, 0, sizeof(p6rd));

    struct ifreq ifr; memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, "sit0", sizeof(ifr.ifr_name)-1);
    ifr.ifr_data = (void*)&p6rd;

    (void)ioctl(s, {cmd}, &ifr);
    close(s); return 0;
}}
""".strip()

for cmd in ["SIOCADD6RD", "SIOCCHG6RD", "SIOCDEL6RD"]:
    wr(f"ipv4_6rd_{cmd.lower()}.c", TPL_6RD.format(common=COMMON, cmd=cmd))