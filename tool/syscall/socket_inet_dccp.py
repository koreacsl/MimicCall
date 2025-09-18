import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_inet_dccp"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <linux/dccp.h>

#ifndef IPPROTO_DCCP
#define IPPROTO_DCCP 33
#endif
#ifndef SOCK_DCCP
#define SOCK_DCCP 6
#endif

static int s4(void){ int s = socket(AF_INET, SOCK_DCCP, IPPROTO_DCCP); if(s<0) return -1; return s; }
static int s6(void){ int s = socket(AF_INET6, SOCK_DCCP, IPPROTO_DCCP); if(s<0) return -1; return s; }
""").lstrip()

BASIC_V4 = COMMON + r"""
int main(void){
    int s = s4(); if(s>=0) close(s);
    return 0;
}
"""
BASIC_V6 = COMMON + r"""
int main(void){
    int s = s6(); if(s>=0) close(s);
    return 0;
}
"""
with open(os.path.join(OUTDIR, "socket_v4.c"), "w") as f: f.write(BASIC_V4)
with open(os.path.join(OUTDIR, "socket_v6.c"), "w") as f: f.write(BASIC_V6)

SET_INT_TPL_V4 = r"""
{common}
int main(void){{
    int s = s4(); if(s<0) return 0;
    int v = 0;
    (void)setsockopt(s, IPPROTO_DCCP, {opt}, &v, sizeof(v));
    close(s); return 0;
}}
""".strip()

GET_INT_TPL_V4 = r"""
{common}
int main(void){{
    int s = s4(); if(s<0) return 0;
    int v = 0; socklen_t l = sizeof(v);
    (void)getsockopt(s, IPPROTO_DCCP, {opt}, &v, &l);
    close(s); return 0;
}}
""".strip()

SET_INT_TPL_V6 = r"""
{common}
int main(void){{
    int s = s6(); if(s<0) return 0;
    int v = 0;
    (void)setsockopt(s, IPPROTO_DCCP, {opt}, &v, sizeof(v));
    close(s); return 0;
}}
""".strip()

GET_INT_TPL_V6 = r"""
{common}
int main(void){{
    int s = s6(); if(s<0) return 0;
    int v = 0; socklen_t l = sizeof(v);
    (void)getsockopt(s, IPPROTO_DCCP, {opt}, &v, &l);
    close(s); return 0;
}}
""".strip()

SET_BUF_TPL_V4 = r"""
{common}
int main(void){{
    int s = s4(); if(s<0) return 0;
    unsigned char b[1] = {{{{0}}}};
    (void)setsockopt(s, IPPROTO_DCCP, {opt}, b, sizeof(b));
    close(s); return 0;
}}
""".strip()

GET_BUF_TPL_V4 = r"""
{common}
int main(void){{
    int s = s4(); if(s<0) return 0;
    unsigned char b[8]; socklen_t l = sizeof(b);
    (void)getsockopt(s, IPPROTO_DCCP, {opt}, b, &l);
    close(s); return 0;
}}
""".strip()

SET_BUF_TPL_V6 = r"""
{common}
int main(void){{
    int s = s6(); if(s<0) return 0;
    unsigned char b[1] = {{{{0}}}};
    (void)setsockopt(s, IPPROTO_DCCP, {opt}, b, sizeof(b));
    close(s); return 0;
}}
""".strip()

GET_BUF_TPL_V6 = r"""
{common}
int main(void){{
    int s = s6(); if(s<0) return 0;
    unsigned char b[8]; socklen_t l = sizeof(b);
    (void)getsockopt(s, IPPROTO_DCCP, {opt}, b, &l);
    close(s); return 0;
}}
""".strip()

int_opts = [
    "DCCP_SOCKOPT_PACKET_SIZE",
    "DCCP_SOCKOPT_CHANGE_L",
    "DCCP_SOCKOPT_CHANGE_R",
    "DCCP_SOCKOPT_GET_CUR_MPS",
    "DCCP_SOCKOPT_SERVER_TIMEWAIT",
    "DCCP_SOCKOPT_SEND_CSCOV",
    "DCCP_SOCKOPT_RECV_CSCOV",
    "DCCP_SOCKOPT_QPOLICY_ID",
    "DCCP_SOCKOPT_QPOLICY_TXQLEN",
]

buf_opts = [
    "DCCP_SOCKOPT_SERVICE",
    "DCCP_SOCKOPT_AVAILABLE_CCIDS",
    "DCCP_SOCKOPT_CCID",
    "DCCP_SOCKOPT_TX_CCID",
    "DCCP_SOCKOPT_RX_CCID",
    "DCCP_SOCKOPT_CCID_RX_INFO",
    "DCCP_SOCKOPT_CCID_TX_INFO",
]

def write(path, src):
    with open(path, "w") as f:
        f.write(src)

for opt in int_opts:
    base = opt.lower().replace("dccp_sockopt_", "")
    write(os.path.join(OUTDIR, f"v4_set_{base}.c"), SET_INT_TPL_V4.format(common=COMMON, opt=opt))
    write(os.path.join(OUTDIR, f"v4_get_{base}.c"), GET_INT_TPL_V4.format(common=COMMON, opt=opt))
    write(os.path.join(OUTDIR, f"v6_set_{base}.c"), SET_INT_TPL_V6.format(common=COMMON, opt=opt))
    write(os.path.join(OUTDIR, f"v6_get_{base}.c"), GET_INT_TPL_V6.format(common=COMMON, opt=opt))

for opt in buf_opts:
    base = opt.lower().replace("dccp_sockopt_", "")
    write(os.path.join(OUTDIR, f"v4_set_{base}.c"), SET_BUF_TPL_V4.format(common=COMMON, opt=opt))
    write(os.path.join(OUTDIR, f"v4_get_{base}.c"), GET_BUF_TPL_V4.format(common=COMMON, opt=opt))
    write(os.path.join(OUTDIR, f"v6_set_{base}.c"), SET_BUF_TPL_V6.format(common=COMMON, opt=opt))
    write(os.path.join(OUTDIR, f"v6_get_{base}.c"), GET_BUF_TPL_V6.format(common=COMMON, opt=opt))
