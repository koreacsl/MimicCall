import os
from textwrap import dedent

OUT = "./tool/cfiles/socket_packet"
os.makedirs(OUT, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <linux/socket.h>
#include <linux/net.h>
#include <linux/if_packet.h>
#include <linux/if_ether.h>
#include <linux/if_arp.h>

#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 02000000
#endif
#ifndef SOCK_NONBLOCK
#define SOCK_NONBLOCK 00004000
#endif

static int mk_pkt(int type){
    return socket(AF_PACKET, type|SOCK_CLOEXEC|SOCK_NONBLOCK, htons(ETH_P_ALL));
}

static void do_bind_with_proto(int s, int proto_be){
    struct sockaddr_ll sa;
    memset(&sa, 0, sizeof(sa));
    sa.sll_family = AF_PACKET;
    sa.sll_protocol = proto_be;
    sa.sll_ifindex = 0;
    sa.sll_hatype = ARPHRD_ETHER;
    sa.sll_pkttype = 0;
    sa.sll_halen = 6;
    (void)bind(s, (struct sockaddr*)&sa, sizeof(sa));
}
""").lstrip()

def write_c(path, body):
    with open(path, "w") as f:
        f.write(body)

for tname in ["SOCK_RAW", "SOCK_DGRAM"]:
    code = COMMON + f"""
int main(void){{
    int s = mk_pkt({tname});
    if (s >= 0) close(s);
    return 0;
}}
"""
    write_c(os.path.join(OUT, f"socket_type_{tname.lower()}.c"), code)

protocols = [
"ETH_P_802_3","ETH_P_AX25","ETH_P_ALL","ETH_P_802_2","ETH_P_SNAP","ETH_P_DDCMP",
"ETH_P_WAN_PPP","ETH_P_PPP_MP","ETH_P_LOCALTALK","ETH_P_CAN","ETH_P_CANFD","ETH_P_PPPTALK",
"ETH_P_TR_802_2","ETH_P_MOBITEX","ETH_P_CONTROL","ETH_P_IRDA","ETH_P_ECONET","ETH_P_HDLC",
"ETH_P_ARCNET","ETH_P_DSA","ETH_P_TRAILER","ETH_P_PHONET","ETH_P_IEEE802154","ETH_P_CAIF","ETH_P_XDSA"
]
for p in protocols:
    code = COMMON + f"""
int main(void){{
    int s = mk_pkt(SOCK_RAW);
    if (s >= 0) {{
        do_bind_with_proto(s, htons({p}));
        close(s);
    }}
    return 0;
}}
"""
    write_c(os.path.join(OUT, f"bind_proto_{p.lower()}.c"), code)

int_opts = [
"PACKET_RECV_OUTPUT","PACKET_COPY_THRESH","PACKET_AUXDATA","PACKET_ORIGDEV","PACKET_VERSION",
"PACKET_HDRLEN","PACKET_RESERVE","PACKET_LOSS","PACKET_VNET_HDR","PACKET_TX_TIMESTAMP",
"PACKET_TIMESTAMP","PACKET_FANOUT","PACKET_TX_HAS_OFF","PACKET_QDISC_BYPASS"
]
for opt in int_opts:
    code = COMMON + f"""
int main(void){{
    int s = mk_pkt(SOCK_RAW);
    if (s < 0) return 0;
    int v = 0; socklen_t vl = sizeof(v);
    (void)setsockopt(s, SOL_PACKET, {opt}, &v, sizeof(v));
    (void)getsockopt(s, SOL_PACKET, {opt}, &v, &vl);
    v = 1;
    (void)setsockopt(s, SOL_PACKET, {opt}, &v, sizeof(v));
    close(s);
    return 0;
}}
"""
    write_c(os.path.join(OUT, f"sockopt_int_{opt.lower()}.c"), code)

buf_opts_simple = ["PACKET_STATISTICS"]
for opt in buf_opts_simple:
    code = COMMON + f"""
int main(void){{
    int s = mk_pkt(SOCK_RAW);
    if (s < 0) return 0;
    char buf[128]; socklen_t bl = sizeof(buf);
    (void)getsockopt(s, SOL_PACKET, {opt}, buf, &bl);
    close(s);
    return 0;
}}
"""
    write_c(os.path.join(OUT, f"sockopt_buf_get_{opt.lower()}.c"), code)

for opt in ["PACKET_RX_RING","PACKET_TX_RING"]:
    code = COMMON + f"""
int main(void){{
    int s = mk_pkt(SOCK_RAW);
    if (s < 0) return 0;
    struct tpacket_req req; memset(&req, 0, sizeof(req));
    (void)setsockopt(s, SOL_PACKET, {opt}, &req, sizeof(req));
    close(s);
    return 0;
}}
"""
    write_c(os.path.join(OUT, f"sockopt_buf_set_{opt.lower()}.c"), code)

for opt in ["PACKET_ADD_MEMBERSHIP","PACKET_DROP_MEMBERSHIP"]:
    code = COMMON + f"""
int main(void){{
    int s = mk_pkt(SOCK_RAW);
    if (s < 0) return 0;
    struct packet_mreq m; memset(&m, 0, sizeof(m));
    m.mr_ifindex = 0; m.mr_type = ARPHRD_ETHER; m.mr_alen = 6;
    (void)setsockopt(s, SOL_PACKET, {opt}, &m, sizeof(m));
    close(s);
    return 0;
}}
"""
    write_c(os.path.join(OUT, f"sockopt_buf_set_{opt.lower()}.c"), code)

code = COMMON + r"""
int main(void){
    int s = mk_pkt(SOCK_RAW);
    if (s < 0) return 0;
    struct sock_fprog prog; memset(&prog, 0, sizeof(prog));
    (void)setsockopt(s, SOL_PACKET, PACKET_FANOUT_DATA, &prog, sizeof(prog));
    char buf[64]; socklen_t bl = sizeof(buf);
    (void)getsockopt(s, SOL_PACKET, PACKET_FANOUT_DATA, buf, &bl);
    close(s);
    return 0;
}
"""
write_c(os.path.join(OUT, "sockopt_buf_packet_fanout_data.c"), code)

fanout_types = [
"PACKET_FANOUT_HASH","PACKET_FANOUT_LB","PACKET_FANOUT_CPU","PACKET_FANOUT_ROLLOVER",
"PACKET_FANOUT_RND","PACKET_FANOUT_QM","PACKET_FANOUT_CBPF","PACKET_FANOUT_EBPF",
"PACKET_FANOUT_FLAG_ROLLOVER","PACKET_FANOUT_FLAG_DEFRAG","PACKET_FANOUT_FLAG_UNIQUEID"
]
for ft in fanout_types:
    code = COMMON + f"""
int main(void){{
    int s = mk_pkt(SOCK_RAW);
    if (s < 0) return 0;
    struct {{ uint16_t id; uint16_t type; }} fan = {{0, 0}};
    fan.type = {ft};
    (void)setsockopt(s, SOL_PACKET, PACKET_FANOUT, &fan, sizeof(fan));
    close(s);
    return 0;
}}
"""
    write_c(os.path.join(OUT, f"fanout_type_{ft.lower()}.c"), code)