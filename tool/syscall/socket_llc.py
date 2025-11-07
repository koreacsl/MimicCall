import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_llc"
os.makedirs(OUTDIR, exist_ok=True)

SOCK_TYPES = ["SOCK_DGRAM", "SOCK_STREAM"]

LLC_OPTS = [
    "LLC_OPT_RETRY",
    "LLC_OPT_SIZE",
    "LLC_OPT_ACK_TMR_EXP",
    "LLC_OPT_P_TMR_EXP",
    "LLC_OPT_REJ_TMR_EXP",
    "LLC_OPT_BUSY_TMR_EXP",
    "LLC_OPT_TX_WIN",
    "LLC_OPT_RX_WIN",
    "LLC_OPT_PKTINFO",
]

OPT_MINVAL = {
    "LLC_OPT_RETRY": 1,
    "LLC_OPT_SIZE": 1,
    "LLC_OPT_ACK_TMR_EXP": 1,
    "LLC_OPT_P_TMR_EXP": 1,
    "LLC_OPT_REJ_TMR_EXP": 1,
    "LLC_OPT_BUSY_TMR_EXP": 1,
    "LLC_OPT_TX_WIN": 1,
    "LLC_OPT_RX_WIN": 1,
    "LLC_OPT_PKTINFO": 1,
}

COMMON = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>

#include <linux/socket.h>
#include <linux/net.h>
#include <linux/if_ether.h>
#include <linux/if_arp.h>
#include <linux/llc.h>

#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 02000000
#endif

static int mk_llc_socket(int type)
{
    int s = socket(AF_LLC, type | SOCK_CLOEXEC, 0);
    if (s >= 0) {
        int fl = fcntl(s, F_GETFL, 0);
        if (fl >= 0) (void)fcntl(s, F_SETFL, fl | O_NONBLOCK);
    }
    return s;
}

static void try_bind(int s)
{
    struct sockaddr_llc sa;
    memset(&sa, 0, sizeof(sa));
    sa.sllc_family = AF_LLC;
    sa.sllc_arphrd = ARPHRD_ETHER;  
    sa.sllc_sap    = 0;
    (void)bind(s, (struct sockaddr *)&sa, sizeof(sa));
}

static void try_setsockopt_getsockopt(int s, int optname, int val)
{
    (void)setsockopt(s, SOL_LLC, optname, &val, sizeof(val));
    int out = 0;
    socklen_t len = sizeof(out);
    (void)getsockopt(s, SOL_LLC, optname, &out, &len);
}
""").lstrip()

def gen_source(sock_type: str, opt: str, val: int) -> str:
    return COMMON + f"""
int main(void)
{{
    int s = mk_llc_socket({sock_type});
    if (s >= 0) {{
        try_bind(s);
        try_setsockopt_getsockopt(s, {opt}, {val});
        close(s);
    }}
    return 0;
}}
"""

def fname(sock_type: str, opt: str) -> str:
    return f"llc_{sock_type.lower()}_{opt.lower()}.c"

for st in SOCK_TYPES:
    for opt in LLC_OPTS:
        src = gen_source(st, opt, OPT_MINVAL[opt])
        with open(os.path.join(OUTDIR, fname(st, opt)), "w") as f:
            f.write(src)

for st in SOCK_TYPES:
    base = COMMON + f"""
int main(void)
{{
    int s = mk_llc_socket({st});
    if (s >= 0) {{
        try_bind(s);
        close(s);
    }}
    return 0;
}}
"""
    with open(os.path.join(OUTDIR, f"llc_{st.lower()}_bind_only.c"), "w") as f:
        f.write(base)
