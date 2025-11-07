import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/netfilter_ipv6"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <linux/socket.h>
#include <linux/netfilter_ipv6/ip6_tables.h>
#include <linux/netfilter_ipv6/ip6t_rt.h>
#include <linux/netfilter_ipv6/ip6t_mh.h>
#include <linux/netfilter_ipv6/ip6t_opts.h>
#include <linux/netfilter_ipv6/ip6t_frag.h>
#include <linux/netfilter_ipv6/ip6t_ipv6header.h>
#include <linux/netfilter_ipv6/ip6t_ah.h>
#include <linux/netfilter_ipv6/ip6t_srh.h>
#include <linux/netfilter_ipv6/ip6t_REJECT.h>
#include <linux/netfilter_ipv6/ip6t_NPT.h>
#include <linux/netfilter_ipv6/ip6t_HL.h>
#include <linux/netfilter/x_tables.h>

#ifndef SOL_IPV6
#define SOL_IPV6 41
#endif

static int ms6(void){ int s = socket(AF_INET6, SOCK_DGRAM, 0); if(s<0) return -1; return s; }
""").lstrip()

SET_REPLACE = COMMON + dedent(r"""
int main(void){
    int s = ms6(); if(s<0) return 0;
    struct {
        struct ip6t_replace rep;
        struct xt_counters ctrs[2];
    } p;
    memset(&p, 0, sizeof(p));
    (void)setsockopt(s, SOL_IPV6, IP6T_SO_SET_REPLACE, &p, sizeof(p));
    close(s);
    return 0;
}
""")

SET_ADD_COUNTERS = COMMON + dedent(r"""
int main(void){
    int s = ms6(); if(s<0) return 0;
    struct {
        /* Corrected from ipt_counters_info to ip6t_counters_info */
        struct ip6t_counters_info ci;
        struct xt_counters c[2];
    } p;
    memset(&p, 0, sizeof(p));
    (void)setsockopt(s, SOL_IPV6, IP6T_SO_SET_ADD_COUNTERS, &p, sizeof(p));
    close(s);
    return 0;
}
""")


GET_ENTRIES = COMMON + dedent(r"""
int main(void){
    int s = ms6(); if(s<0) return 0;
    struct {
        /* Corrected from ipt_get_entries to ip6t_get_entries */
        struct ip6t_get_entries ge;
        unsigned char buf[16];
    } p;
    socklen_t l = sizeof(p);
    memset(&p, 0, sizeof(p));
    p.ge.size = sizeof(p.buf);
    (void)getsockopt(s, SOL_IPV6, IP6T_SO_GET_ENTRIES, &p, &l);
    close(s);
    return 0;
}
""")

GET_REV_MATCH = COMMON + dedent(r"""
int main(void){
    int s = ms6(); if(s<0) return 0;
    struct xt_get_revision rev; socklen_t l=sizeof(rev);
    memset(&rev, 0, sizeof(rev));
    (void)getsockopt(s, SOL_IPV6, IP6T_SO_GET_REVISION_MATCH, &rev, &l);
    close(s);
    return 0;
}
""")

GET_REV_TARGET = COMMON + dedent(r"""
int main(void){
    int s = ms6(); if(s<0) return 0;
    struct xt_get_revision rev; socklen_t l=sizeof(rev);
    memset(&rev, 0, sizeof(rev));
    (void)getsockopt(s, SOL_IPV6, IP6T_SO_GET_REVISION_TARGET, &rev, &l);
    close(s);
    return 0;
}
""")

with open(os.path.join(OUTDIR, "set_replace.c"), "w") as f: f.write(SET_REPLACE)
with open(os.path.join(OUTDIR, "set_add_counters.c"), "w") as f: f.write(SET_ADD_COUNTERS)
with open(os.path.join(OUTDIR, "get_entries.c"), "w") as f: f.write(GET_ENTRIES)
with open(os.path.join(OUTDIR, "get_revision_match.c"), "w") as f: f.write(GET_REV_MATCH)
with open(os.path.join(OUTDIR, "get_revision_target.c"), "w") as f: f.write(GET_REV_TARGET)

def write_flag(basename: str, body: str):
    with open(os.path.join(OUTDIR, basename), "w") as f:
        f.write(COMMON + body)

ip6_flags = ["IP6T_F_PROTO","IP6T_F_TOS","IP6T_F_GOTO"]
for fl in ip6_flags:
    body = f"""
int main(void){{
    struct ip6t_ip6 x; memset(&x,0,sizeof(x));
    x.flags = {fl};
    (void)x.flags; /* Use variable to prevent unused warning */
    return 0;
}}
"""
    write_flag(f"flag_ip6_{fl.lower().replace('ip6t_f_','')}.c", body)

ip6_invflags = ["IP6T_INV_VIA_IN","IP6T_INV_VIA_OUT","IP6T_INV_TOS","IP6T_INV_SRCIP","IP6T_INV_DSTIP","IP6T_INV_FRAG","IP6T_INV_PROTO"]
for fl in ip6_invflags:
    body = f"""
int main(void){{
    struct ip6t_ip6 x; memset(&x,0,sizeof(x));
    x.invflags = {fl};
    (void)x.invflags;
    return 0;
}}
"""
    write_flag(f"flag_ip6_inv_{fl.lower().replace('ip6t_inv_','')}.c", body)

rt_flags = ["IP6T_RT_TYP","IP6T_RT_SGS","IP6T_RT_LEN","IP6T_RT_RES","IP6T_RT_FST_MASK","IP6T_RT_FST","IP6T_RT_FST_NSTRICT"]
for fl in rt_flags:
    body = f"""
int main(void){{
    struct ip6t_rt x; memset(&x,0,sizeof(x));
    x.flags = {fl};
    (void)x.flags;
    return 0;
}}
"""
    write_flag(f"flag_rt_{fl.lower().replace('ip6t_rt_','')}.c", body)

rt_invflags = ["IP6T_RT_INV_TYP","IP6T_RT_INV_SGS","IP6T_RT_INV_LEN"]
for fl in rt_invflags:
    body = f"""
int main(void){{
    struct ip6t_rt x; memset(&x,0,sizeof(x));
    x.invflags = {fl};
    (void)x.invflags;
    return 0;
}}
"""
    write_flag(f"flag_rt_inv_{fl.lower().replace('ip6t_rt_inv_','')}.c", body)

opts_flags = ["IP6T_OPTS_LEN","IP6T_OPTS_OPTS","IP6T_OPTS_NSTRICT"]
for fl in opts_flags:
    body = f"""
int main(void){{
    struct ip6t_opts x; memset(&x,0,sizeof(x));
    x.flags = {fl};
    (void)x.flags;
    return 0;
}}
"""
    write_flag(f"flag_opts_{fl.lower().replace('ip6t_opts_','')}.c", body)

opts_invflags = ["IP6T_OPTS_INV_LEN"]
for fl in opts_invflags:
    body = f"""
int main(void){{
    struct ip6t_opts x; memset(&x,0,sizeof(x));
    x.invflags = {fl};
    (void)x.invflags;
    return 0;
}}
"""
    write_flag(f"flag_opts_inv_{fl.lower().replace('ip6t_opts_inv_','')}.c", body)

frag_flags = ["IP6T_FRAG_IDS","IP6T_FRAG_LEN","IP6T_FRAG_RES","IP6T_FRAG_FST","IP6T_FRAG_MF","IP6T_FRAG_NMF"]
for fl in frag_flags:
    body = f"""
int main(void){{
    struct ip6t_frag x; memset(&x,0,sizeof(x));
    x.flags = {fl};
    (void)x.flags;
    return 0;
}}
"""
    write_flag(f"flag_frag_{fl.lower().replace('ip6t_frag_','')}.c", body)

frag_invflags = ["IP6T_FRAG_INV_IDS","IP6T_FRAG_INV_LEN"]
for fl in frag_invflags:
    body = f"""
int main(void){{
    struct ip6t_frag x; memset(&x,0,sizeof(x));
    x.invflags = {fl};
    (void)x.invflags;
    return 0;
}}
"""
    write_flag(f"flag_frag_inv_{fl.lower().replace('ip6t_frag_inv_','')}.c", body)

ipv6hdr_flags = ["MASK_HOPOPTS","MASK_DSTOPTS","MASK_ROUTING","MASK_FRAGMENT","MASK_AH","MASK_ESP","MASK_NONE","MASK_PROTO"]
for fl in ipv6hdr_flags:
    body = f"""
int main(void){{
    struct ip6t_ipv6header_info x; memset(&x,0,sizeof(x));
    x.matchflags = {fl};
    (void)x.matchflags;
    return 0;
}}
"""
    write_flag(f"flag_ipv6header_match_{fl.lower().replace('mask_','')}.c", body)

for fl in ipv6hdr_flags:
    body = f"""
int main(void){{
    struct ip6t_ipv6header_info x; memset(&x,0,sizeof(x));
    x.invflags = {fl};
    (void)x.invflags;
    return 0;
}}
"""
    write_flag(f"flag_ipv6header_inv_{fl.lower().replace('mask_','')}.c", body)

ah_flags = ["IP6T_AH_INV_SPI","IP6T_AH_INV_LEN"]
for fl in ah_flags:
    body = f"""
int main(void){{
    struct ip6t_ah x; memset(&x,0,sizeof(x));
    x.invflags = {fl};
    (void)x.invflags;
    return 0;
}}
"""
    write_flag(f"flag_ah_inv_{fl.lower().replace('ip6t_ah_inv_','')}.c", body)

srh_flags = ["IP6T_SRH_NEXTHDR","IP6T_SRH_LEN_EQ","IP6T_SRH_LEN_GT","IP6T_SRH_LEN_LT","IP6T_SRH_SEGS_EQ","IP6T_SRH_SEGS_GT","IP6T_SRH_SEGS_LT","IP6T_SRH_LAST_EQ","IP6T_SRH_LAST_GT","IP6T_SRH_LAST_LT","IP6T_SRH_TAG","IP6T_SRH_PSID","IP6T_SRH_NSID","IP6T_SRH_LSID"]
for fl in srh_flags:
    body = f"""
int main(void){{
    struct ip6t_srh x; memset(&x,0,sizeof(x));
    x.mt_flags = {fl};
    (void)x.mt_flags;
    return 0;
}}
"""
    write_flag(f"flag_srh_{fl.lower().replace('ip6t_srh_','')}.c", body)

for fl in srh_flags:
    body = f"""
int main(void){{
    struct ip6t_srh x; memset(&x,0,sizeof(x));
    x.mt_invflags = {fl};
    (void)x.mt_invflags;
    return 0;
}}
"""
    write_flag(f"flag_srh_inv_{fl.lower().replace('ip6t_srh_','')}.c", body)

reject_with = ["IP6T_ICMP6_NO_ROUTE","IP6T_ICMP6_ADM_PROHIBITED","IP6T_ICMP6_NOT_NEIGHBOUR","IP6T_ICMP6_ADDR_UNREACH","IP6T_ICMP6_PORT_UNREACH","IP6T_ICMP6_ECHOREPLY","IP6T_TCP_RESET","IP6T_ICMP6_POLICY_FAIL","IP6T_ICMP6_REJECT_ROUTE"]
for fl in reject_with:
    body = f"""
int main(void){{
    struct ip6t_reject_info x; memset(&x,0,sizeof(x));
    x.with = {fl};
    (void)x.with;
    return 0;
}}
"""
    write_flag(f"flag_reject_{fl.lower().replace('ip6t_icmp6_','icmp6_').replace('ip6t_tcp_','tcp_')}.c", body)
