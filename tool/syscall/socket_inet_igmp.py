import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_inet_igmp"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include <linux/ip.h>
#include <linux/ipv6.h>
#include <linux/route.h>
#include <linux/sockios.h>
#include <linux/if.h>
#include <linux/in.h>
#include <linux/in6.h>

#include <linux/mroute.h>
#include <linux/mroute6.h>

#ifndef SOL_IP
#define SOL_IP 0
#endif
#ifndef SOL_IPV6
#define SOL_IPV6 41
#endif
#ifndef IPPROTO_IGMP
#define IPPROTO_IGMP 2
#endif

static int s4(void){ int s=socket(AF_INET,  SOCK_RAW, IPPROTO_IGMP); if(s<0) return -1; return s; }
static int s6(void){ int s=socket(AF_INET6, SOCK_RAW, IPPROTO_IGMP); if(s<0) return -1; return s; }
""").lstrip()

def write(name, src):
    with open(os.path.join(OUTDIR, name), "w") as f:
        f.write(src)

write("socket_v4.c", COMMON + r"""
int main(void){ int s=s4(); if(s>=0) close(s); return 0; }
""")
write("socket_v6.c", COMMON + r"""
int main(void){ int s=s6(); if(s>=0) close(s); return 0; }
""")

write("mrt_init.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0; int v=0;
    (void)setsockopt(s, SOL_IP, MRT_INIT, &v, sizeof(v));
    close(s); return 0;
}
""")
write("mrt_done.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    (void)setsockopt(s, SOL_IP, MRT_DONE, NULL, 0);
    close(s); return 0;
}
""")
for op in ["MRT_ADD_VIF","MRT_DEL_VIF"]:
    write(f"{op.lower()}.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    struct vifctl v; memset(&v, 0, sizeof(v));
    (void)setsockopt(s, SOL_IP, %s, &v, sizeof(v));
    close(s); return 0;
}
""" % op)

for op in ["MRT_ADD_MFC","MRT_DEL_MFC","MRT_ADD_MFC_PROXY","MRT_DEL_MFC_PROXY"]:
    write(f"{op.lower()}.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    struct mfcctl m; memset(&m, 0, sizeof(m));
    (void)setsockopt(s, SOL_IP, %s, &m, sizeof(m));
    close(s); return 0;
}
""" % op)

mrt_flush_flags = ["MRT_FLUSH_MFC","MRT_FLUSH_MFC_STATIC","MRT_FLUSH_VIFS","MRT_FLUSH_VIFS_STATIC"]
for fl in mrt_flush_flags:
    write(f"mrt_flush_{fl.lower().replace('mrt_flush_','')}.c", COMMON + f"""
int main(void){{
    int s=s4(); if(s<0) return 0;
    int v = {fl};
    (void)setsockopt(s, SOL_IP, MRT_FLUSH, &v, sizeof(v));
    close(s); return 0;
}}
""")

write("mrt_assert.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    int v = 0;
    (void)setsockopt(s, SOL_IP, MRT_ASSERT, &v, sizeof(v));
    close(s); return 0;
}
""")

write("mrt_pim.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    int v = 0;
    (void)setsockopt(s, SOL_IP, MRT_ASSERT, &v, sizeof(v));
    close(s); return 0;
}
""")

mrt_tables = ["RT_TABLE_UNSPEC","RT_TABLE_COMPAT","RT_TABLE_DEFAULT","RT_TABLE_MAIN","RT_TABLE_LOCAL","RT_TABLE_MAX","1"]
for tbl in mrt_tables:
    tag = tbl.lower().replace("rt_table_","tbl_").replace("1","tbl_1")
    write(f"mrt_table_{tag}.c", COMMON + f"""
int main(void){{
    int s=s4(); if(s<0) return 0;
    int v = {tbl};
    (void)setsockopt(s, SOL_IP, MRT_ASSERT, &v, sizeof(v));
    close(s); return 0;
}}
""")

mrt_gets = ["MRT_VERSION","MRT_PIM","MRT_ASSERT"]
for g in mrt_gets:
    write(f"mrt_get_{g.lower().replace('mrt_','')}.c", COMMON + f"""
int main(void){{
    int s=s4(); if(s<0) return 0;
    int v=0; socklen_t l=sizeof(v);
    (void)getsockopt(s, SOL_IP, {g}, &v, &l);
    close(s); return 0;
}}
""")

write("ioctl_siocgetvifcnt.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    struct sioc_vif_req r; memset(&r, 0, sizeof(r));
    (void)ioctl(s, SIOCGETVIFCNT, &r);
    close(s); return 0;
}
""")
write("ioctl_siocgetsgcnt.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    struct sioc_sg_req r; memset(&r, 0, sizeof(r));
    (void)ioctl(s, SIOCGETSGCNT, &r);
    close(s); return 0;
}
""")

write("mrt6_init.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0; int v=0;
    (void)setsockopt(s, SOL_IPV6, MRT6_INIT, &v, sizeof(v));
    close(s); return 0;
}
""")
write("mrt6_done.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    (void)setsockopt(s, SOL_IPV6, MRT6_DONE, NULL, 0);
    close(s); return 0;
}
""")
for op in ["MRT6_ADD_MIF","MRT6_DEL_MIF"]:
    write(f"{op.lower()}.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    struct mif6ctl m; memset(&m, 0, sizeof(m));
    (void)setsockopt(s, SOL_IPV6, %s, &m, sizeof(m));
    close(s); return 0;
}
""" % op)

for op in ["MRT6_ADD_MFC","MRT6_DEL_MFC","MRT6_ADD_MFC_PROXY","MRT6_DEL_MFC_PROXY"]:
    write(f"{op.lower()}.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    struct mf6cctl m; memset(&m, 0, sizeof(m));
    (void)setsockopt(s, SOL_IPV6, %s, &m, sizeof(m));
    close(s); return 0;
}
""" % op)

mrt6_flush_flags = ["MRT6_FLUSH_MFC","MRT6_FLUSH_MFC_STATIC","MRT6_FLUSH_MIFS","MRT6_FLUSH_MIFS_STATIC"]
for fl in mrt6_flush_flags:
    write(f"mrt6_flush_{fl.lower().replace('mrt6_flush_','')}.c", COMMON + f"""
int main(void){{
    int s=s6(); if(s<0) return 0;
    int v = {fl};
    (void)setsockopt(s, SOL_IPV6, MRT6_FLUSH, &v, sizeof(v));
    close(s); return 0;
}}
""")

write("mrt6_assert.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    int v=0;
    (void)setsockopt(s, SOL_IPV6, MRT6_ASSERT, &v, sizeof(v));
    close(s); return 0;
}
""")
write("mrt6_pim.c", COMMON + r"""
int main(void){
    int s=s6(); if(s<0) return 0;
    int v=0;
    (void)setsockopt(s, SOL_IPV6, MRT6_ASSERT, &v, sizeof(v));
    close(s); return 0;
}
""")

for tbl in mrt_tables:
    tag = tbl.lower().replace("rt_table_","tbl_").replace("1","tbl_1")
    write(f"mrt6_table_{tag}.c", COMMON + f"""
int main(void){{
    int s=s6(); if(s<0) return 0;
    int v = {tbl};
    (void)setsockopt(s, SOL_IPV6, MRT6_ASSERT, &v, sizeof(v));
    close(s); return 0;
}}
""")

mrt6_gets = ["MRT6_VERSION","MRT6_PIM","MRT6_ASSERT"]
for g in mrt6_gets:
    write(f"mrt6_get_{g.lower().replace('mrt6_','')}.c", COMMON + f"""
int main(void){{
    int s=s6(); if(s<0) return 0;
    int v=0; socklen_t l=sizeof(v);
    (void)getsockopt(s, SOL_IPV6, {g}, &v, &l);
    close(s); return 0;
}}
""")

write("ioctl_siocgetmifcnt_in6.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    struct sioc_mif_req6 r; memset(&r, 0, sizeof(r));
    (void)ioctl(s, SIOCGETMIFCNT_IN6, &r);
    close(s); return 0;
}
""")
write("ioctl_siocgetsgcnt_in6.c", COMMON + r"""
int main(void){
    int s=s4(); if(s<0) return 0;
    struct sioc_sg_req6 r; memset(&r, 0, sizeof(r));
    (void)ioctl(s, SIOCGETSGCNT_IN6, &r);
    close(s); return 0;
}
""")

