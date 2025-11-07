import os
from textwrap import dedent

OUTPUT_DIR = "./tool/cfiles/netfilter_arp"
os.makedirs(OUTPUT_DIR, exist_ok=True)

COMMON_HEADERS = dedent(r"""
    #include <stdint.h>
    #include <string.h>
    #include <unistd.h>
    #include <sys/types.h>
    #include <sys/socket.h>
    #include <linux/socket.h>
    #include <linux/netfilter_arp/arp_tables.h>
    #include <linux/netfilter_arp/arpt_mangle.h>

    #ifndef SOL_IP
    #define SOL_IP 0
    #endif

    static int make_sock(void){
        int s = socket(AF_INET, SOCK_DGRAM, 0);
        if(s < 0) return -1;
        return s;
    }
""").lstrip()

SO_SET_REPLACE = (COMMON_HEADERS + dedent(r"""
    int main(void){
        int s = make_sock();
        if(s < 0) return 0;

        struct arpt_replace repl;
        memset(&repl, 0, sizeof(repl));
        strncpy(repl.name, "filter", sizeof(repl.name)-1);
        repl.valid_hooks = (1u<<NF_ARP_IN)|(1u<<NF_ARP_OUT)|(1u<<NF_ARP_FORWARD);
        repl.num_entries = 0;
        repl.size = 0;
        repl.num_counters = 0;
        repl.counters = (void*)0;

        (void)setsockopt(s, SOL_IP, ARPT_SO_SET_REPLACE, &repl, sizeof(repl));
        close(s);
        return 0;
    }
"""))

SO_SET_ADD_COUNTERS = (COMMON_HEADERS + dedent(r"""
    int main(void){
        int s = make_sock();
        if(s < 0) return 0;

        struct {
            struct arpt_counters_info ci;
            struct xt_counters ctrs[4];
        } pack;
        memset(&pack, 0, sizeof(pack));
        strncpy(pack.ci.name, "filter", sizeof(pack.ci.name)-1);
        pack.ci.num_counters = 4;

        (void)setsockopt(s, SOL_IP, ARPT_SO_SET_ADD_COUNTERS, &pack, sizeof(pack));
        close(s);
        return 0;
    }
"""))

SO_GET_INFO = (COMMON_HEADERS + dedent(r"""
    int main(void){
        int s = make_sock();
        if(s < 0) return 0;

        struct arpt_getinfo info;
        socklen_t len = sizeof(info);
        memset(&info, 0, sizeof(info));
        strncpy(info.name, "filter", sizeof(info.name)-1);

        (void)getsockopt(s, SOL_IP, ARPT_SO_GET_INFO, &info, &len);
        close(s);
        return 0;
    }
"""))

SO_GET_ENTRIES = (COMMON_HEADERS + dedent(r"""
    int main(void){
        int s = make_sock();
        if(s < 0) return 0;

        struct {
            struct arpt_get_entries ge;
            unsigned char buf[16];
        } pack;
        socklen_t len = sizeof(pack);
        memset(&pack, 0, sizeof(pack));
        strncpy(pack.ge.name, "filter", sizeof(pack.ge.name)-1);
        pack.ge.size = sizeof(pack.buf);

        (void)getsockopt(s, SOL_IP, ARPT_SO_GET_ENTRIES, &pack, &len);
        close(s);
        return 0;
    }
"""))

SO_GET_REVISION_TARGET = (COMMON_HEADERS + dedent(r"""
    int main(void){
        int s = make_sock();
        if(s < 0) return 0;

        struct xt_get_revision rev;
        socklen_t len = sizeof(rev);
        memset(&rev, 0, sizeof(rev));
        strncpy(rev.name, "mangle", sizeof(rev.name)-1);

        (void)getsockopt(s, SOL_IP, ARPT_SO_GET_REVISION_TARGET, &rev, &len);
        close(s);
        return 0;
    }
"""))

REPLACE_INVFLAG_TPL = r"""
{headers}
int main(void){{
    int s = make_sock();
    if(s < 0) return 0;

    struct arpt_replace repl;
    memset(&repl, 0, sizeof(repl));
    strncpy(repl.name, "filter", sizeof(repl.name)-1);
    repl.valid_hooks = (1u<<NF_ARP_IN)|(1u<<NF_ARP_OUT)|(1u<<NF_ARP_FORWARD);

    struct arpt_arp a;
    memset(&a, 0, sizeof(a));
    a.invflags = {flag};

    (void)setsockopt(s, SOL_IP, ARPT_SO_SET_REPLACE, &repl, sizeof(repl));
    close(s);
    return 0;
}}
""".strip()

REPLACE_MANGLEFLAG_TPL = r"""
{headers}
int main(void){{
    int s = make_sock();
    if(s < 0) return 0;

    struct arpt_replace repl;
    memset(&repl, 0, sizeof(repl));
    strncpy(repl.name, "filter", sizeof(repl.name)-1);
    repl.valid_hooks = (1u<<NF_ARP_IN)|(1u<<NF_ARP_OUT)|(1u<<NF_ARP_FORWARD);

    struct arpt_mangle m;
    memset(&m, 0, sizeof(m));
    m.flags = {flag};

    (void)setsockopt(s, SOL_IP, ARPT_SO_SET_REPLACE, &repl, sizeof(repl));
    close(s);
    return 0;
}}
""".strip()

REPLACE_TARGET_TPL = r"""
{headers}
int main(void){{
    int s = make_sock();
    if(s < 0) return 0;

    struct arpt_replace repl;
    memset(&repl, 0, sizeof(repl));
    strncpy(repl.name, "filter", sizeof(repl.name)-1);
    repl.valid_hooks = (1u<<NF_ARP_IN)|(1u<<NF_ARP_OUT)|(1u<<NF_ARP_FORWARD);

    struct arpt_mangle m;
    memset(&m, 0, sizeof(m));
    m.target = {flag};

    (void)setsockopt(s, SOL_IP, ARPT_SO_SET_REPLACE, &repl, sizeof(repl));
    close(s);
    return 0;
}}
""".strip()

arp_invflags = [
    "ARPT_INV_VIA_IN",
    "ARPT_INV_VIA_OUT",
    "ARPT_INV_SRCIP",
    "ARPT_INV_TGTIP",
    "ARPT_INV_SRCDEVADDR",
    "ARPT_INV_TGTDEVADDR",
    "ARPT_INV_ARPOP",
    "ARPT_INV_ARPHRD",
    "ARPT_INV_ARPPRO",
    "ARPT_INV_ARPHLN",
]

mangle_flags = [
    "ARPT_MANGLE_SDEV",
    "ARPT_MANGLE_TDEV",
    "ARPT_MANGLE_SIP",
    "ARPT_MANGLE_TIP",
    "ARPT_MANGLE_MASK",
]

mangle_targets = [
    "NF_DROP",
    "NF_ACCEPT",
    "XT_CONTINUE",
]

with open(os.path.join(OUTPUT_DIR, "set_replace.c"), "w") as f:
    f.write(SO_SET_REPLACE)
with open(os.path.join(OUTPUT_DIR, "set_add_counters.c"), "w") as f:
    f.write(SO_SET_ADD_COUNTERS)
with open(os.path.join(OUTPUT_DIR, "get_info.c"), "w") as f:
    f.write(SO_GET_INFO)
with open(os.path.join(OUTPUT_DIR, "get_entries.c"), "w") as f:
    f.write(SO_GET_ENTRIES)
with open(os.path.join(OUTPUT_DIR, "get_revision_target.c"), "w") as f:
    f.write(SO_GET_REVISION_TARGET)

for fl in arp_invflags:
    fname = f"replace_inv_{fl.lower().replace('arpt_inv_','')}.c"
    with open(os.path.join(OUTPUT_DIR, fname), "w") as f:
        f.write(REPLACE_INVFLAG_TPL.format(headers=COMMON_HEADERS, flag=fl))

for fl in mangle_flags:
    fname = f"replace_mangleflag_{fl.lower().replace('arpt_mangle_','')}.c"
    with open(os.path.join(OUTPUT_DIR, fname), "w") as f:
        f.write(REPLACE_MANGLEFLAG_TPL.format(headers=COMMON_HEADERS, flag=fl))

for fl in mangle_targets:
    fname = f"replace_target_{fl.lower().replace('nf_','').replace('xt_','')}.c"
    with open(os.path.join(OUTPUT_DIR, fname), "w") as f:
        f.write(REPLACE_TARGET_TPL.format(headers=COMMON_HEADERS, flag=fl))
