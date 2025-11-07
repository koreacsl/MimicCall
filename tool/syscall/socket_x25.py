import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_x25"
os.makedirs(OUTDIR, exist_ok=True)

ACCEPT_FLAG_SETS = [
    ("none", "0"),
    ("cloexec", "SOCK_CLOEXEC"),
    ("nonblock", "SOCK_NONBLOCK"),
    ("cloexec_nonblock", "(SOCK_CLOEXEC|SOCK_NONBLOCK)"),
]

ACCEPT4_C_TMPL = dedent(r"""
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/route.h>
#include <linux/net.h>
#include <linux/socket.h>
#include <linux/sockios.h>
#include <linux/x25.h>

static void fill_x25_addr(struct sockaddr_x25* sa){
    memset(sa, 0, sizeof(*sa));
    sa->sx25_family = AF_X25;
    memcpy(&sa->sx25_addr, "                ", 16);
}

int main(void){
    int s = socket(AF_X25, SOCK_SEQPACKET|SOCK_CLOEXEC, 0);
    if (s >= 0){
        struct sockaddr_x25 sa;
        fill_x25_addr(&sa);

        (void)bind(s, (struct sockaddr*)&sa, sizeof(sa));
        (void)connect(s, (struct sockaddr*)&sa, sizeof(sa));

        (void)accept4(s, NULL, NULL, ACCFLAGS);

        int v = 0;
        (void)setsockopt(s, SOL_X25, X25_QBITINCL, &v, sizeof(v));
        socklen_t l = sizeof(v);
        (void)getsockopt(s, SOL_X25, X25_QBITINCL, &v, &l);

        struct x25_route_struct rt; memset(&rt, 0, sizeof(rt));
        (void)ioctl(s, SIOCADDRT, &rt);
        (void)ioctl(s, SIOCDELRT, &rt);

        struct x25_subscrip_struct sub; memset(&sub, 0, sizeof(sub));
        (void)ioctl(s, SIOCX25GSUBSCRIP, &sub);
        (void)ioctl(s, SIOCX25SSUBSCRIP, &sub);

        struct x25_facilities fac; memset(&fac, 0, sizeof(fac));
        (void)ioctl(s, SIOCX25SFACILITIES, &fac);
        (void)ioctl(s, SIOCX25GFACILITIES, &fac);

        struct x25_dte_facilities dte; memset(&dte, 0, sizeof(dte));
        (void)ioctl(s, SIOCX25SDTEFACILITIES, &dte);
        (void)ioctl(s, SIOCX25GDTEFACILITIES, &dte);

        struct x25_calluserdata cud; memset(&cud, 0, sizeof(cud));
        (void)ioctl(s, SIOCX25SCALLUSERDATA, &cud);
        (void)ioctl(s, SIOCX25GCALLUSERDATA, &cud);

        struct x25_causediag cd; memset(&cd, 0, sizeof(cd));
        (void)ioctl(s, SIOCX25SCAUSEDIAG, &cd);
        (void)ioctl(s, SIOCX25GCAUSEDIAG, &cd);

        struct x25_subaddr suba; memset(&suba, 0, sizeof(suba));
        (void)ioctl(s, SIOCX25SCUDMATCHLEN, &suba);

        (void)ioctl(s, SIOCX25CALLACCPTAPPRV, 0);
        (void)ioctl(s, SIOCX25SENDCALLACCPT, 0);

        close(s);
    }
    return 0;
}
""").lstrip()

for name, flags in ACCEPT_FLAG_SETS:
    csrc = ACCEPT4_C_TMPL.replace("ACCFLAGS", flags)
    with open(os.path.join(OUTDIR, f"x25_accept4_{name}.c"), "w") as f:
        f.write(csrc)

FAC_REVERSE_SETS = [
    ("rev0", "0"),
    ("rev81", "0x81"),
]

FAC_C_TMPL = dedent(r"""
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <linux/net.h>
#include <linux/socket.h>
#include <linux/sockios.h>
#include <linux/x25.h>

static void fill_x25_addr(struct sockaddr_x25* sa){
    memset(sa, 0, sizeof(*sa));
    sa->sx25_family = AF_X25;
    memcpy(&sa->sx25_addr, "                ", 16);
}

int main(void){
    int s = socket(AF_X25, SOCK_SEQPACKET|SOCK_CLOEXEC, 0);
    if (s >= 0){
        struct sockaddr_x25 sa;
        fill_x25_addr(&sa);
        (void)bind(s, (struct sockaddr*)&sa, sizeof(sa));

        struct x25_facilities fac;
        memset(&fac, 0, sizeof(fac));
        fac.reverse = REVERSEFLAG;
        (void)ioctl(s, SIOCX25SFACILITIES, &fac);
        (void)ioctl(s, SIOCX25GFACILITIES, &fac);

        close(s);
    }
    return 0;
}
""").lstrip()

for name, val in FAC_REVERSE_SETS:
    csrc = FAC_C_TMPL.replace("REVERSEFLAG", val)
    with open(os.path.join(OUTDIR, f"x25_fac_reverse_{name}.c"), "w") as f:
        f.write(csrc)
