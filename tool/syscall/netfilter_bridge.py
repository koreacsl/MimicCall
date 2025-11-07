import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/netfilter_bridge"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <linux/socket.h>
#include <linux/netfilter/x_tables.h>
#include <linux/netfilter_bridge.h>
#include <linux/netfilter_bridge/ebtables.h>
#include <linux/netfilter_bridge/ebt_802_3.h>
#include <linux/netfilter_bridge/ebt_among.h>
#include <linux/netfilter_bridge/ebt_arp.h>
#include <linux/netfilter_bridge/ebt_ip.h>
#include <linux/netfilter_bridge/ebt_ip6.h>
#include <linux/netfilter_bridge/ebt_limit.h>
#include <linux/netfilter_bridge/ebt_mark_m.h>
#include <linux/netfilter_bridge/ebt_pkttype.h>
#include <linux/netfilter_bridge/ebt_stp.h>
#include <linux/netfilter_bridge/ebt_vlan.h>
#include <linux/netfilter_bridge/ebt_arpreply.h>
#include <linux/netfilter_bridge/ebt_nat.h>
#include <linux/netfilter_bridge/ebt_log.h>
#include <linux/netfilter_bridge/ebt_mark_t.h>
#include <linux/netfilter_bridge/ebt_nflog.h>
#include <linux/netfilter_bridge/ebt_redirect.h>

#ifndef SOL_IP
#define SOL_IP 0
#endif

static int ms(void){ int s = socket(AF_INET, SOCK_DGRAM, 0); if(s<0) return -1; return s; }
""").lstrip()

SET_ENTRIES = COMMON + dedent(r"""
int main(void){
    int s = ms(); if(s<0) return 0;
    // Using a valid struct for setsockopt, e.g., ebt_replace, even if empty
    struct ebt_replace repl;
    memset(&repl, 0, sizeof(repl));
    (void)setsockopt(s, SOL_IP, EBT_SO_SET_ENTRIES, &repl, sizeof(repl));
    close(s);
    return 0;
}
""")

SET_COUNTERS = COMMON + dedent(r"""
int main(void){
    int s = ms(); if(s<0) return 0;
    struct {
        struct ebt_counters_info ci;
        struct xt_counters c[1];
    } p;
    memset(&p, 0, sizeof(p));
    (void)setsockopt(s, SOL_IP, EBT_SO_SET_COUNTERS, &p, sizeof(p));
    close(s);
    return 0;
}
""")

GET_ENTRIES = COMMON + dedent(r"""
int main(void){
    int s = ms(); if(s<0) return 0;
    struct {
        struct ebt_get_entries ge;
        unsigned char buf[16];
        struct xt_counters c[1];
    } p;
    socklen_t l = sizeof(p);
    memset(&p, 0, sizeof(p));
    p.ge.entries_size = sizeof(p.buf);
    p.ge.num_counters = 1;
    (void)getsockopt(s, SOL_IP, EBT_SO_GET_ENTRIES, &p, &l);
    close(s);
    return 0;
}
""")

GET_INIT_ENTRIES = COMMON + dedent(r"""
int main(void){
    int s = ms(); if(s<0) return 0;
    struct {
        struct ebt_get_entries ge;
        unsigned char buf[16];
        struct xt_counters c[1];
    } p;
    socklen_t l = sizeof(p);
    memset(&p, 0, sizeof(p));
    p.ge.entries_size = sizeof(p.buf);
    p.ge.num_counters = 1;
    (void)getsockopt(s, SOL_IP, EBT_SO_GET_INIT_ENTRIES, &p, &l);
    close(s);
    return 0;
}
""")

with open(os.path.join(OUTDIR, "set_entries.c"), "w") as f: f.write(SET_ENTRIES)
with open(os.path.join(OUTDIR, "set_counters.c"), "w") as f: f.write(SET_COUNTERS)
with open(os.path.join(OUTDIR, "get_entries.c"), "w") as f: f.write(GET_ENTRIES)
with open(os.path.join(OUTDIR, "get_init_entries.c"), "w") as f: f.write(GET_INIT_ENTRIES)


def write_flag_test(basename: str, body: str):
    with open(os.path.join(OUTDIR, basename), "w") as f:
        f.write(COMMON + body)

entry_bitmask_flags = ["EBT_NOPROTO_F","EBT_802_3_F","EBT_SOURCEMAC_F","EBT_DESTMAC_F"]
for fl in entry_bitmask_flags:
    body = f"""
int main(void){{
    struct ebt_entry e; memset(&e, 0, sizeof(e));
    e.bitmask = {fl};
    (void)e.bitmask; /* Use the variable to avoid unused warning */
    return 0;
}}
"""
    write_flag_test(f"flag_entry_bitmask_{fl.lower()}.c", body)

entry_invflags = ["EBT_IPROTO","EBT_IIN","EBT_IOUT","EBT_ISOURCE","EBT_IDEST","EBT_ILOGICALIN","EBT_ILOGICALOUT"]
for fl in entry_invflags:
    body = f"""
int main(void){{
    struct ebt_entry e; memset(&e, 0, sizeof(e));
    e.invflags = {fl};
    (void)e.invflags;
    return 0;
}}
"""
    write_flag_test(f"flag_entry_inv_{fl.lower()}.c", body)

entries_policy = ["EBT_DROP","EBT_ACCEPT","EBT_RETURN"]
for fl in entries_policy:
    body = f"""
int main(void){{
    struct ebt_entries et; memset(&et, 0, sizeof(et));
    et.policy = {fl};
    (void)et.policy;
    return 0;
}}
"""
    write_flag_test(f"flag_entries_policy_{fl.lower()}.c", body)

verdicts = ["EBT_DROP","EBT_ACCEPT","EBT_RETURN","EBT_CONTINUE"]
for fl in verdicts:
    body = f"""
int main(void){{
    int v = {fl};
    (void)v;
    return 0;
}}
"""
    write_flag_test(f"flag_verdict_{fl.lower()}.c", body)

f8023 = ["EBT_802_3_SAP","EBT_802_3_TYPE","EBT_802_3"]
for fl in f8023:
    body = f"""
int main(void){{
    struct ebt_802_3_info x; memset(&x, 0, sizeof(x));
    x.bitmask = {fl};
    (void)x.bitmask;
    return 0;
}}
"""
    write_flag_test(f"flag_802_3_{fl.lower().replace('ebt_802_3_','')}.c", body)

among_flags = ["EBT_AMONG_DST_NEG","EBT_AMONG_SRC_NEG"]
for fl in among_flags:
    body = f"""
int main(void){{
    struct ebt_among_info x; memset(&x, 0, sizeof(x));
    x.bitmask = {fl};
    (void)x.bitmask;
    return 0;
}}
"""
    write_flag_test(f"flag_among_{fl.lower().replace('ebt_among_','')}.c", body)

arp_flags = ["EBT_ARP_OPCODE","EBT_ARP_HTYPE","EBT_ARP_PTYPE","EBT_ARP_SRC_IP","EBT_ARP_DST_IP","EBT_ARP_SRC_MAC","EBT_ARP_DST_MAC","EBT_ARP_GRAT"]
for fl in arp_flags:
    body = f"""
int main(void){{
    struct ebt_arp_info x; memset(&x, 0, sizeof(x));
    x.bitmask = {fl};
    (void)x.bitmask;
    return 0;
}}
"""
    write_flag_test(f"flag_arp_{fl.lower().replace('ebt_arp_','')}.c", body)

ip_flags = ["EBT_IP_SOURCE","EBT_IP_DEST","EBT_IP_TOS","EBT_IP_PROTO","EBT_IP_SPORT","EBT_IP_DPORT"]
for fl in ip_flags:
    body = f"""
int main(void){{
    struct ebt_ip_info x; memset(&x, 0, sizeof(x));
    x.bitmask = {fl};
    (void)x.bitmask;
    return 0;
}}
"""
    write_flag_test(f"flag_ip_{fl.lower().replace('ebt_ip_','')}.c", body)

ip6_flags = ["EBT_IP6_SOURCE","EBT_IP6_DEST","EBT_IP6_TCLASS","EBT_IP6_PROTO","EBT_IP6_SPORT","EBT_IP6_DPORT","EBT_IP6_ICMP6"]
for fl in ip6_flags:
    body = f"""
int main(void){{
    struct ebt_ip6_info x; memset(&x, 0, sizeof(x));
    x.bitmask = {fl};
    (void)x.bitmask;
    return 0;
}}
"""
    write_flag_test(f"flag_ip6_{fl.lower().replace('ebt_ip6_','')}.c", body)

mark_m_flags = ["EBT_MARK_AND","EBT_MARK_OR"]
for fl in mark_m_flags:
    body = f"""
int main(void){{
    struct ebt_mark_m_info x; memset(&x, 0, sizeof(x));
    x.bitmask = {fl};
    (void)x.bitmask;
    return 0;
}}
"""
    write_flag_test(f"flag_mark_m_{fl.lower().replace('ebt_mark_','')}.c", body)

stp_flags = ["EBT_STP_TYPE","EBT_STP_FLAGS","EBT_STP_ROOTPRIO","EBT_STP_ROOTADDR","EBT_STP_ROOTCOST","EBT_STP_SENDERPRIO","EBT_STP_SENDERADDR","EBT_STP_PORT","EBT_STP_MSGAGE","EBT_STP_MAXAGE","EBT_STP_HELLOTIME","EBT_STP_FWDD"]
for fl in stp_flags:
    body = f"""
int main(void){{
    struct ebt_stp_info x; memset(&x, 0, sizeof(x));
    x.bitmask = {fl};
    (void)x.bitmask;
    return 0;
}}
"""
    write_flag_test(f"flag_stp_{fl.lower().replace('ebt_stp_','')}.c", body)

vlan_flags = ["EBT_VLAN_ID","EBT_VLAN_PRIO","EBT_VLAN_ENCAP"]
for fl in vlan_flags:
    body = f"""
int main(void){{
    struct ebt_vlan_info x; memset(&x, 0, sizeof(x));
    x.bitmask = {fl};
    (void)x.bitmask;
    return 0;
}}
"""
    write_flag_test(f"flag_vlan_{fl.lower().replace('ebt_vlan_','')}.c", body)

log_bits = ["EBT_LOG_IP","EBT_LOG_ARP","EBT_LOG_NFLOG","EBT_LOG_IP6"]
for fl in log_bits:
    body = f"""
int main(void){{
    struct ebt_log_info x; memset(&x, 0, sizeof(x));
    x.bitmask = {fl};
    (void)x.bitmask;
    return 0;
}}
"""
    write_flag_test(f"flag_log_{fl.lower().replace('ebt_log_','')}.c", body)

mark_marks = ["MARK_SET_VALUE","MARK_OR_VALUE","MARK_AND_VALUE","MARK_XOR_VALUE"]
for fl in mark_marks:
    body = f"""
int main(void){{
    struct ebt_mark_t_info x; memset(&x, 0, sizeof(x));
    x.mark = 0; x.target = EBT_ACCEPT;
    (void){fl};
    (void)x; /* Use the variable to avoid unused warning */
    return 0;
}}
"""
    write_flag_test(f"flag_mark_t_{fl.lower().replace('mark_','')}.c", body)
