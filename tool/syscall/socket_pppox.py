import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_pppox"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>

#include <linux/net.h>
#include <linux/if_pppox.h>
#include <linux/ppp-ioctl.h>
#include <linux/if_pppol2tp.h>

#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 02000000
#endif
#ifndef SOCK_NONBLOCK
#define SOCK_NONBLOCK 00004000
#endif

static int s_pppoe(void){
    return socket(AF_PPPOX, SOCK_STREAM|SOCK_CLOEXEC|SOCK_NONBLOCK, PX_PROTO_OE);
}
static int s_pppol2tp(void){
    return socket(AF_PPPOX, SOCK_STREAM|SOCK_CLOEXEC|SOCK_NONBLOCK, PX_PROTO_OL2TP);
}
static int s_pptp(void){
    return socket(AF_PPPOX, SOCK_STREAM|SOCK_CLOEXEC|SOCK_NONBLOCK, PX_PROTO_PPTP);
}

static void fill_pppoe(struct sockaddr_pppox *sa){
    memset(sa, 0, sizeof(*sa));
    sa->sa_family   = AF_PPPOX;
    sa->sa_protocol = PX_PROTO_OE;
}
static void fill_pppol2tp(struct sockaddr_pppol2tp *sa){
    memset(sa, 0, sizeof(*sa));
    sa->sa_family   = AF_PPPOX;
    sa->sa_protocol = PX_PROTO_OL2TP;
}
static void fill_pppol2tpin6(struct sockaddr_pppol2tpin6 *sa){
    memset(sa, 0, sizeof(*sa));
    sa->sa_family   = AF_PPPOX;
    sa->sa_protocol = PX_PROTO_OL2TP;
}
static void fill_pppol2tpv3(struct sockaddr_pppol2tpv3 *sa){
    memset(sa, 0, sizeof(*sa));
    sa->sa_family   = AF_PPPOX;
    sa->sa_protocol = PX_PROTO_OL2TP;
}
static void fill_pppol2tpv3in6(struct sockaddr_pppol2tpv3in6 *sa){
    memset(sa, 0, sizeof(*sa));
    sa->sa_family   = AF_PPPOX;
    sa->sa_protocol = PX_PROTO_OL2TP;
}
static void fill_pptp(struct sockaddr_pppox *sa){
    memset(sa, 0, sizeof(*sa));
    sa->sa_family   = AF_PPPOX;
    sa->sa_protocol = PX_PROTO_PPTP;
}
""").lstrip()

def w(name, body):
    with open(os.path.join(OUTDIR, name), "w") as f:
        f.write(body)

w("pppoe_basic.c", COMMON + r"""
int main(void){
    int s = s_pppoe();
    if (s < 0) return 0;

    struct sockaddr_pppox sa;
    fill_pppoe(&sa);
    (void)connect(s, (struct sockaddr*)&sa, sizeof(sa));
    (void)ioctl(s, PPPOEIOCSFWD, &sa);
    (void)ioctl(s, PPPOEIOCDFWD, 0);

    close(s);
    return 0;
}
""")

w("pppol2tp_v2_ipv4_basic.c", COMMON + r"""
int main(void){
    int s = s_pppol2tp();
    if (s < 0) return 0;

    struct sockaddr_pppol2tp sa;
    fill_pppol2tp(&sa);
    (void)connect(s, (struct sockaddr*)&sa, sizeof(sa));

    int v = 0;
    (void)ioctl(s, PPPIOCGCHAN, &v);
    (void)ioctl(s, PPPIOCGFLAGS, &v);
    (void)ioctl(s, PPPIOCSFLAGS, &v);
    (void)ioctl(s, PPPIOCGMRU, &v);
    (void)ioctl(s, PPPIOCSMRU, &v);

    char stats[8] = {0};
    (void)ioctl(s, PPPIOCGL2TPSTATS, stats);

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    (void)ioctl(s, SIOCGIFMTU, &ifr);
    (void)ioctl(s, SIOCSIFMTU, &ifr);

    int i32 = 0;
    (void)setsockopt(s, SOL_PPPOL2TP, PPPOL2TP_SO_DEBUG, &i32, sizeof(i32));
    (void)setsockopt(s, SOL_PPPOL2TP, PPPOL2TP_SO_RECVSEQ, &i32, sizeof(i32));
    (void)setsockopt(s, SOL_PPPOL2TP, PPPOL2TP_SO_SENDSEQ, &i32, sizeof(i32));
    (void)setsockopt(s, SOL_PPPOL2TP, PPPOL2TP_SO_LNSMODE, &i32, sizeof(i32));
    (void)setsockopt(s, SOL_PPPOL2TP, PPPOL2TP_SO_REORDERTO, &i32, sizeof(i32));

    close(s);
    return 0;
}
""")

w("pppol2tp_v2_ipv6_basic.c", COMMON + r"""
int main(void){
    int s = s_pppol2tp();
    if (s < 0) return 0;

    struct sockaddr_pppol2tpin6 sa;
    fill_pppol2tpin6(&sa);
    (void)connect(s, (struct sockaddr*)&sa, sizeof(sa));

    close(s);
    return 0;
}
""")

w("pppol2tp_v3_ipv4_basic.c", COMMON + r"""
int main(void){
    int s = s_pppol2tp();
    if (s < 0) return 0;

    struct sockaddr_pppol2tpv3 sa;
    fill_pppol2tpv3(&sa);
    (void)connect(s, (struct sockaddr*)&sa, sizeof(sa));

    close(s);
    return 0;
}
""")

w("pppol2tp_v3_ipv6_basic.c", COMMON + r"""
int main(void){
    int s = s_pppol2tp();
    if (s < 0) return 0;

    struct sockaddr_pppol2tpv3in6 sa;
    fill_pppol2tpv3in6(&sa);
    (void)connect(s, (struct sockaddr*)&sa, sizeof(sa));

    close(s);
    return 0;
}
""")

w("pptp_basic.c", COMMON + r"""
int main(void){
    int s = s_pptp();
    if (s < 0) return 0;

    struct sockaddr_pppox sa;
    fill_pptp(&sa);
    (void)bind(s, (struct sockaddr*)&sa, sizeof(sa));
    (void)connect(s, (struct sockaddr*)&sa, sizeof(sa));

    close(s);
    return 0;
}
""")

w("pppox_common_ioctls.c", COMMON + r"""
int main(void){
    int s = s_pppoe();
    if (s < 0) return 0;

    int v = 0;
    (void)ioctl(s, PPPIOCGCHAN, &v);
    (void)ioctl(s, PPPIOCGFLAGS, &v);
    (void)ioctl(s, PPPIOCSFLAGS, &v);
    (void)ioctl(s, PPPIOCGMRU, &v);
    (void)ioctl(s, PPPIOCSMRU, &v);

    close(s);
    return 0;
}
""")

ppp_flag_names = [
    "SC_COMP_PROT","SC_COMP_AC","SC_COMP_TCP","SC_NO_TCP_CCID","SC_REJ_COMP_AC",
    "SC_REJ_COMP_TCP","SC_CCP_OPEN","SC_CCP_UP","SC_ENABLE_IP","SC_LOOP_TRAFFIC",
    "SC_MULTILINK","SC_MP_SHORTSEQ","SC_COMP_RUN","SC_DECOMP_RUN","SC_MP_XSHORTSEQ",
    "SC_DEBUG","SC_LOG_INPKT","SC_LOG_OUTPKT","SC_LOG_RAWIN","SC_LOG_FLUSH",
    "SC_SYNC","SC_MUST_COMP","SC_RCV_B7_0","SC_RCV_B7_1","SC_RCV_EVNP","SC_RCV_ODDP",
]

for name in ppp_flag_names:
    cfile = f"ppp_flag_{name}.c"
    body = COMMON + f"""
int main(void){{
    int s = s_pppoe();
    if (s < 0) return 0;
    int fl = {name};
    (void)ioctl(s, PPPIOCSFLAGS, &fl);
    close(s);
    return 0;
}}
"""
    w(cfile, body)
