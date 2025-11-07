import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/netfilter_ipv4"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <linux/socket.h>
#include <linux/netfilter/xt_osf.h>
#include <linux/netfilter_ipv4/ip_tables.h>
#include <linux/netfilter_ipv4/ipt_ah.h>
#include <linux/netfilter_ipv4/ipt_ttl.h>
#include <linux/netfilter_ipv4/ipt_REJECT.h>
#include <linux/netfilter_ipv4/ipt_ECN.h>
#include <linux/netfilter_ipv4/ipt_TTL.h>
#include <linux/netfilter_ipv4/ipt_CLUSTERIP.h>

#ifndef SOL_IP
#define SOL_IP 0
#endif

static int ms(void){ int s = socket(AF_INET, SOCK_DGRAM, 0); if(s<0) return -1; return s; }
""").lstrip()

SET_REPLACE = COMMON + dedent(r"""
int main(void){
    int s = ms(); if(s<0) return 0;
    struct {
        struct ipt_replace rep;
        struct xt_counters ctrs[2];
    } p;
    memset(&p, 0, sizeof(p));
    (void)setsockopt(s, SOL_IP, IPT_SO_SET_REPLACE, &p, sizeof(p));
    close(s);
    return 0;
}
""")

SET_ADD_COUNTERS = COMMON + dedent(r"""
int main(void){
    int s = ms(); if(s<0) return 0;
    struct {
        struct ipt_counters_info ci;
        struct xt_counters c[2];
    } p;
    memset(&p, 0, sizeof(p));
    (void)setsockopt(s, SOL_IP, IPT_SO_SET_ADD_COUNTERS, &p, sizeof(p));
    close(s);
    return 0;
}
""")

GET_INFO = COMMON + dedent(r"""
int main(void){
    int s = ms(); if(s<0) return 0;
    struct ipt_getinfo gi; socklen_t l=sizeof(gi);
    memset(&gi, 0, sizeof(gi));
    (void)getsockopt(s, SOL_IP, IPT_SO_GET_INFO, &gi, &l);
    close(s);
    return 0;
}
""")

GET_ENTRIES = COMMON + dedent(r"""
int main(void){
    int s = ms(); if(s<0) return 0;
    struct {
        struct ipt_get_entries ge;
        unsigned char buf[16];
    } p;
    socklen_t l = sizeof(p);
    memset(&p, 0, sizeof(p));
    p.ge.size = sizeof(p.buf);
    (void)getsockopt(s, SOL_IP, IPT_SO_GET_ENTRIES, &p, &l);
    close(s);
    return 0;
}
""")

GET_REV_MATCH = COMMON + dedent(r"""
int main(void){
    int s = ms(); if(s<0) return 0;
    struct xt_get_revision rev; socklen_t l=sizeof(rev);
    memset(&rev, 0, sizeof(rev));
    (void)getsockopt(s, SOL_IP, IPT_SO_GET_REVISION_MATCH, &rev, &l);
    close(s);
    return 0;
}
""")

GET_REV_TARGET = COMMON + dedent(r"""
int main(void){
    int s = ms(); if(s<0) return 0;
    struct xt_get_revision rev; socklen_t l=sizeof(rev);
    memset(&rev, 0, sizeof(rev));
    (void)getsockopt(s, SOL_IP, IPT_SO_GET_REVISION_TARGET, &rev, &l);
    close(s);
    return 0;
}
""")

with open(os.path.join(OUTDIR, "set_replace.c"), "w") as f: f.write(SET_REPLACE)
with open(os.path.join(OUTDIR, "set_add_counters.c"), "w") as f: f.write(SET_ADD_COUNTERS)
with open(os.path.join(OUTDIR, "get_info.c"), "w") as f: f.write(GET_INFO)
with open(os.path.join(OUTDIR, "get_entries.c"), "w") as f: f.write(GET_ENTRIES)
with open(os.path.join(OUTDIR, "get_revision_match.c"), "w") as f: f.write(GET_REV_MATCH)
with open(os.path.join(OUTDIR, "get_revision_target.c"), "w") as f: f.write(GET_REV_TARGET)

def write_flag_test(basename: str, body: str):
    with open(os.path.join(OUTDIR, basename), "w") as f:
        f.write(COMMON + body)

ipt_ip_flags = ["IPT_F_FRAG","IPT_F_GOTO"]
for fl in ipt_ip_flags:
    body = f"""
int main(void){{
    int s=ms(); if(s<0) return 0;
    struct ipt_ip ip; memset(&ip,0,sizeof(ip));
    ip.flags = {fl};
    struct ipt_getinfo gi; socklen_t l=sizeof(gi); memset(&gi,0,sizeof(gi));
    (void)getsockopt(s,SOL_IP,IPT_SO_GET_INFO,&gi,&l);
    (void)ip.flags; close(s); return 0;
}}
"""
    write_flag_test(f"flag_ipt_ip_{fl.lower().replace('ipt_f_','')}.c", body)

ipt_ip_invflags = ["IPT_INV_VIA_IN","IPT_INV_VIA_OUT","IPT_INV_TOS","IPT_INV_SRCIP","IPT_INV_DSTIP","IPT_INV_FRAG","IPT_INV_PROTO"]
for fl in ipt_ip_invflags:
    body = f"""
int main(void){{
    int s=ms(); if(s<0) return 0;
    struct ipt_ip ip; memset(&ip,0,sizeof(ip));
    ip.invflags = {fl};
    struct ipt_getinfo gi; socklen_t l=sizeof(gi); memset(&gi,0,sizeof(gi));
    (void)getsockopt(s,SOL_IP,IPT_SO_GET_INFO,&gi,&l);
    (void)ip.invflags; close(s); return 0;
}}
"""
    write_flag_test(f"flag_ipt_ip_inv_{fl.lower().replace('ipt_inv_','')}.c", body)

osf_flags = ["XT_OSF_GENRE","XT_OSF_TTL","XT_OSF_LOG","XT_OSF_INVERT"]
for fl in osf_flags:
    body = f"""
int main(void){{
    int s=ms(); if(s<0) return 0;
    struct xt_osf_info x; memset(&x,0,sizeof(x));
    x.flags = {fl};
    struct ipt_getinfo gi; socklen_t l=sizeof(gi); memset(&gi,0,sizeof(gi));
    (void)getsockopt(s,SOL_IP,IPT_SO_GET_INFO,&gi,&l);
    (void)x.flags; close(s); return 0;
}}
"""
    write_flag_test(f"flag_osf_{fl.lower().replace('xt_osf_','')}.c", body)

ttl_modes = ["IPT_TTL_EQ","IPT_TTL_NE","IPT_TTL_LT","IPT_TTL_GT"]
for fl in ttl_modes:
    body = f"""
int main(void){{
    int s=ms(); if(s<0) return 0;
    struct ipt_ttl_info t; memset(&t,0,sizeof(t));
    t.mode = {fl};
    t.ttl = 1;
    struct ipt_getinfo gi; socklen_t l=sizeof(gi); memset(&gi,0,sizeof(gi));
    (void)getsockopt(s,SOL_IP,IPT_SO_GET_INFO,&gi,&l);
    (void)t.mode; close(s); return 0;
}}
"""
    write_flag_test(f"flag_ttl_mode_{fl.lower().replace('ipt_ttl_','')}.c", body)

reject_with = [
    "IPT_ICMP_NET_UNREACHABLE","IPT_ICMP_HOST_UNREACHABLE","IPT_ICMP_PROT_UNREACHABLE",
    "IPT_ICMP_PORT_UNREACHABLE","IPT_ICMP_NET_PROHIBITED","IPT_ICMP_HOST_PROHIBITED",
    "IPT_TCP_RESET","IPT_ICMP_ADMIN_PROHIBITED"
]
for fl in reject_with:
    body = f"""
int main(void){{
    int s=ms(); if(s<0) return 0;
    struct ipt_reject_info r; memset(&r,0,sizeof(r));
    r.with = {fl};
    struct ipt_getinfo gi; socklen_t l=sizeof(gi); memset(&gi,0,sizeof(gi));
    (void)getsockopt(s,SOL_IP,IPT_SO_GET_INFO,&gi,&l);
    (void)r.with; close(s); return 0;
}}
"""
    write_flag_test(f"flag_reject_{fl.lower().replace('ipt_icmp_','icmp_').replace('ipt_tcp_','tcp_')}.c", body)

ecn_ops = ["IPT_ECN_OP_SET_IP","IPT_ECN_OP_SET_ECE","IPT_ECN_OP_SET_CWR"]
for fl in ecn_ops:
    body = f"""
int main(void){{
    int s=ms(); if(s<0) return 0;
    struct ipt_ECN_info e; memset(&e,0,sizeof(e));
    e.operation = {fl};
    struct ipt_getinfo gi; socklen_t l=sizeof(gi); memset(&gi,0,sizeof(gi));
    (void)getsockopt(s,SOL_IP,IPT_SO_GET_INFO,&gi,&l);
    (void)e.operation; close(s); return 0;
}}
"""
    write_flag_test(f"flag_ecn_{fl.lower().replace('ipt_ecn_op_set_','')}.c", body)

cluster_hash = ["CLUSTERIP_HASHMODE_SIP","CLUSTERIP_HASHMODE_SIP_SPT","CLUSTERIP_HASHMODE_SIP_SPT_DPT"]
for fl in cluster_hash:
    body = f"""
int main(void){{
    int s=ms(); if(s<0) return 0;
    struct ipt_clusterip_tgt_info c; memset(&c,0,sizeof(c));
    c.hash_mode = {fl};
    struct ipt_getinfo gi; socklen_t l=sizeof(gi); memset(&gi,0,sizeof(gi));
    (void)getsockopt(s,SOL_IP,IPT_SO_GET_INFO,&gi,&l);
    (void)c.hash_mode; close(s); return 0;
}}
"""
    write_flag_test(f"flag_clusterip_hash_{fl.lower().replace('clusterip_hashmode_','')}.c", body)
