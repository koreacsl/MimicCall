import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_inet_icmp"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include <linux/icmp.h>
#include <linux/icmpv6.h>

#ifndef IPPROTO_ICMP
#define IPPROTO_ICMP 1
#endif
#ifndef IPPROTO_ICMPV6
#define IPPROTO_ICMPV6 58
#endif
#ifndef SOCK_DGRAM
#define SOCK_DGRAM 2
#endif
#ifndef SOCK_RAW
#define SOCK_RAW 3
#endif
#ifndef AF_INET
#define AF_INET 2
#endif
#ifndef AF_INET6
#define AF_INET6 10
#endif

static int s4_dgram(void){ int s = socket(AF_INET,  SOCK_DGRAM, IPPROTO_ICMP);  if(s<0) return -1; return s; }
static int s4_raw(void)  { int s = socket(AF_INET,  SOCK_RAW,   IPPROTO_ICMP);  if(s<0) return -1; return s; }
static int s6_dgram(void){ int s = socket(AF_INET6, SOCK_DGRAM, IPPROTO_ICMPV6);if(s<0) return -1; return s; }
static int s6_raw(void)  { int s = socket(AF_INET6, SOCK_RAW,   IPPROTO_ICMPV6);if(s<0) return -1; return s; }
""").lstrip()

V4_DGRAM = COMMON + r"""
int main(void){
    int s = s4_dgram(); if(s>=0) close(s);
    return 0;
}
"""
V4_RAW = COMMON + r"""
int main(void){
    int s = s4_raw(); if(s>=0) close(s);
    return 0;
}
"""
V6_DGRAM = COMMON + r"""
int main(void){
    int s = s6_dgram(); if(s>=0) close(s);
    return 0;
}
"""
V6_RAW = COMMON + r"""
int main(void){
    int s = s6_raw(); if(s>=0) close(s);
    return 0;
}
"""

with open(os.path.join(OUTDIR, "socket_v4_dgram.c"), "w") as f: f.write(V4_DGRAM)
with open(os.path.join(OUTDIR, "socket_v4_raw.c"),   "w") as f: f.write(V4_RAW)
with open(os.path.join(OUTDIR, "socket_v6_dgram.c"), "w") as f: f.write(V6_DGRAM)
with open(os.path.join(OUTDIR, "socket_v6_raw.c"),   "w") as f: f.write(V6_RAW)

SET_FILTER_V4 = COMMON + r"""
int main(void){
    int s = s4_dgram(); if(s<0) return 0;
    struct icmp_filter flt; memset(&flt, 0, sizeof(flt));
    (void)setsockopt(s, IPPROTO_ICMP, ICMP_FILTER, &flt, sizeof(flt));
    close(s); return 0;
}
"""
SET_FILTER_V6 = COMMON + r"""
int main(void){
    int s = s6_dgram(); if(s<0) return 0;
    struct icmp_filter flt; memset(&flt, 0, sizeof(flt));
    (void)setsockopt(s, IPPROTO_ICMP, ICMP_FILTER, &flt, sizeof(flt));
    close(s); return 0;
}
"""

with open(os.path.join(OUTDIR, "set_icmp_filter_v4.c"), "w") as f: f.write(SET_FILTER_V4)
with open(os.path.join(OUTDIR, "set_icmp_filter_v6.c"), "w") as f: f.write(SET_FILTER_V6)