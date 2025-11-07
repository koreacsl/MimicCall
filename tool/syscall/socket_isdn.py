import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_isdn"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>

#include <linux/socket.h>
#include <linux/mISDNif.h>
#include <linux/isdn/capiutil.h>
#include <uapi/linux/capi.h>
#include <uapi/linux/isdn/capicmd.h>

#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 02000000
#endif

static int s_isdn_base(void){
    int s = socket(AF_ISDN, SOCK_RAW|SOCK_CLOEXEC, ISDN_P_BASE);
    if (s >= 0) {
        int fl = fcntl(s, F_GETFL, 0);
        if (fl >= 0) fcntl(s, F_SETFL, fl | O_NONBLOCK);
    }
    return s;
}

static int s_isdn_proto(int proto){
    int s = socket(AF_ISDN, SOCK_RAW|SOCK_CLOEXEC, proto);
    if (s >= 0) {
        int fl = fcntl(s, F_GETFL, 0);
        if (fl >= 0) fcntl(s, F_SETFL, fl | O_NONBLOCK);
    }
    return s;
}

static void fill_addr(struct sockaddr_mISDN *sa){
    memset(sa, 0, sizeof(*sa));
    sa->family = AF_ISDN;
    sa->dev = 0;
    sa->channel = 0;
    sa->sapi = 0;
    sa->tei = 0;
}
""").lstrip()

def wr(name: str, src: str):
    with open(os.path.join(OUTDIR, name), "w") as f:
        f.write(src)

wr("isdn_base_bind.c", COMMON + r"""
int main(void){
    int s = s_isdn_base(); if (s < 0) return 0;
    struct sockaddr_mISDN sa; fill_addr(&sa);
    (void)bind(s, (struct sockaddr*)&sa, sizeof(sa));
    close(s);
    return 0;
}
""")

wr("ioctl_imgetversion.c", COMMON + r"""
int main(void){
    int s = s_isdn_base(); if (s < 0) return 0;
    int32_t v = 0;
    (void)ioctl(s, IMGETVERSION, &v);
    close(s);
    return 0;
}
""")

wr("ioctl_imgetcount.c", COMMON + r"""
int main(void){
    int s = s_isdn_base(); if (s < 0) return 0;
    int32_t cnt = 0;
    (void)ioctl(s, IMGETCOUNT, &cnt);
    close(s);
    return 0;
}
""")

wr("ioctl_imgetdevinfo.c", COMMON + r"""
int main(void){
    int s = s_isdn_base(); if (s < 0) return 0;
    struct mISDN_devinfo di; memset(&di, 0, sizeof(di));
    di.id = 0;
    (void)ioctl(s, IMGETDEVINFO, &di);
    close(s);
    return 0;
}
""")

wr("ioctl_imsetdevname.c", COMMON + r"""
int main(void){
    int s = s_isdn_base(); if (s < 0) return 0;
    struct mISDN_devrename rn; memset(&rn, 0, sizeof(rn));
    rn.id = 0;
    /* name must be NUL-terminated inside the fixed array; strncpy is fine */
    strncpy((char*)rn.name, "syz0", sizeof(rn.name)-1);
    (void)ioctl(s, IMSETDEVNAME, &rn);
    close(s);
    return 0;
}
""")

isdn_protos = [
    ("ISDN_P_TE_S0",),
    ("ISDN_P_NT_S0",),
    ("ISDN_P_TE_E1",),
    ("ISDN_P_NT_E1",),
    ("ISDN_P_LAPD_TE",),
    ("ISDN_P_LAPD_NT",),
    ("ISDN_P_B_RAW",),
    ("ISDN_P_B_HDLC",),
    ("ISDN_P_B_X75SLP",),
    ("ISDN_P_B_L2DTMF",),
    ("ISDN_P_B_L2DSP",),
    ("ISDN_P_B_L2DSPHDLC",),
]

TPL_PROTO_MIN = r"""
{common}
int main(void){
    int s = s_isdn_proto({proto}); if (s < 0) return 0;
    struct sockaddr_mISDN sa; fill_addr(&sa);
    (void)bind(s, (struct sockaddr*)&sa, sizeof(sa));
    close(s);
    return 0;
}
""".strip()

for (proto,) in isdn_protos:
    wr(f"isdn_proto_bind_{proto.lower()}.c", TPL_PROTO_MIN.format(common=COMMON, proto=proto))

wr("setsockopt_misdn_time_stamp.c", COMMON + r"""
int main(void){
    int s = s_isdn_proto(ISDN_P_TE_S0); if (s < 0) return 0;
    int v = 1;
    (void)setsockopt(s, 0, MISDN_TIME_STAMP, &v, sizeof(v));
    close(s);
    return 0;
}
""")

wr("getsockopt_misdn_time_stamp.c", COMMON + r"""
int main(void){
    int s = s_isdn_proto(ISDN_P_TE_S0); if (s < 0) return 0;
    int v = 0; socklen_t l = sizeof(v);
    (void)getsockopt(s, 0, MISDN_TIME_STAMP, &v, &l);
    close(s);
    return 0;
}
""")

wr("sendto_misdnhead.c", COMMON + r"""
int main(void){
    int s = s_isdn_proto(ISDN_P_TE_S0); if (s < 0) return 0;
    struct sockaddr_mISDN sa; fill_addr(&sa);
    struct mISDNhead h; memset(&h, 0, sizeof(h));
    (void)sendto(s, &h, sizeof(h), 0, (struct sockaddr*)&sa, sizeof(sa));
    close(s);
    return 0;
}
""")

wr("ioctl_imclear_l2.c", COMMON + r"""
int main(void){
    int s = s_isdn_proto(ISDN_P_TE_S0); if (s < 0) return 0;
    int32_t ch = 0;
    (void)ioctl(s, IMCLEAR_L2, &ch);
    close(s);
    return 0;
}
""")

wr("ioctl_imhold_l1.c", COMMON + r"""
int main(void){
    int s = s_isdn_proto(ISDN_P_TE_S0); if (s < 0) return 0;
    int32_t v = 0;
    (void)ioctl(s, IMHOLD_L1, &v);
    close(s);
    return 0;
}
""")

ctrl_ops = [
    "MISDN_CTRL_GETOP","MISDN_CTRL_LOOP","MISDN_CTRL_CONNECT","MISDN_CTRL_DISCONNECT",
    "MISDN_CTRL_RX_BUFFER","MISDN_CTRL_PCMCONNECT","MISDN_CTRL_PCMDISCONNECT",
    "MISDN_CTRL_SETPEER","MISDN_CTRL_UNSETPEER","MISDN_CTRL_RX_OFF","MISDN_CTRL_FILL_EMPTY",
    "MISDN_CTRL_GETPEER","MISDN_CTRL_L1_TIMER3","MISDN_CTRL_HW_FEATURES_OP",
    "MISDN_CTRL_HW_FEATURES","MISDN_CTRL_HFC_OP","MISDN_CTRL_HFC_PCM_CONN",
    "MISDN_CTRL_HFC_PCM_DISC","MISDN_CTRL_HFC_CONF_JOIN","MISDN_CTRL_HFC_CONF_SPLIT",
    "MISDN_CTRL_HFC_RECEIVE_OFF","MISDN_CTRL_HFC_RECEIVE_ON","MISDN_CTRL_HFC_ECHOCAN_ON",
    "MISDN_CTRL_HFC_ECHOCAN_OFF","MISDN_CTRL_HFC_WD_INIT","MISDN_CTRL_HFC_WD_RESET",
]

TPL_CTRL = r"""
{common}
int main(void){
    int s = s_isdn_proto(ISDN_P_TE_S0); if (s < 0) return 0;
    struct mISDN_ctrl_req rq; memset(&rq, 0, sizeof(rq));
    rq.op = {op};
    (void)ioctl(s, IMCTRLREQ, &rq);
    close(s);
    return 0;
}
""".strip()

for op in ctrl_ops:
    wr(f"ioctl_imctrlreq_{op.lower()}.c", TPL_CTRL.format(common=COMMON, op=op))

COMMON_CAPI = COMMON + r"""
static int open_rdwr(const char* p){
    int fd = open(p, O_RDWR|O_CLOEXEC);
    if (fd >= 0) {
        int fl = fcntl(fd, F_GETFL, 0);
        if (fl >= 0) fcntl(fd, F_SETFL, fl | O_NONBLOCK);
    }
    return fd;
}
"""

wr("capi_write_command.c", COMMON_CAPI + r"""
int main(void){
    int fd = open_rdwr("/dev/capi20"); if (fd < 0) return 0;
    struct capi20_command c; memset(&c, 0, sizeof(c));
    c.len = sizeof(c);
    c.appid = 1;
    c.command = CAPI_ALERT;
    c.subcommand = CAPI_REQ;
    (void)write(fd, &c, sizeof(c));
    close(fd);
    return 0;
}
""")

wr("capi_write_command_data.c", COMMON_CAPI + r"""
int main(void){
    int fd = open_rdwr("/dev/capi20"); if (fd < 0) return 0;
    struct capi20_command_data cd; memset(&cd, 0, sizeof(cd));
    cd.header.len = sizeof(cd.header);
    cd.header.appid = 1;
    cd.header.command = CAPI_INFO;
    cd.header.subcommand = CAPI_REQ;
    (void)write(fd, &cd, sizeof(cd));
    close(fd);
    return 0;
}
""")

wr("capi_ioctl_register.c", COMMON_CAPI + r"""
int main(void){
    int fd = open_rdwr("/dev/capi20"); if (fd < 0) return 0;
    struct capi_register_params p; memset(&p, 0, sizeof(p));
    p.level3cnt = 1; p.datablkcnt = 1; p.datablklen = 64;
    (void)ioctl(fd, CAPI_REGISTER, &p);
    close(fd);
    return 0;
}
""")

for name, code in [
    ("capi_ioctl_get_serial.c", "CAPI_GET_SERIAL"),
    ("capi_ioctl_get_profile.c", "CAPI_GET_PROFILE"),
    ("capi_ioctl_get_manufacturer.c", "CAPI_GET_MANUFACTURER"),
]:
    wr(name, COMMON_CAPI + f"""
int main(void){{
    int fd = open_rdwr("/dev/capi20"); if (fd < 0) return 0;
    int32_t c = 0;
    (void)ioctl(fd, {code}, &c);
    close(fd);
    return 0;
}}
""")

wr("capi_ioctl_get_errcode.c", COMMON_CAPI + r"""
int main(void){
    int fd = open_rdwr("/dev/capi20"); if (fd < 0) return 0;
    int32_t e = 0;
    (void)ioctl(fd, CAPI_GET_ERRCODE, &e);
    close(fd);
    return 0;
}
""")

wr("capi_ioctl_installed.c", COMMON_CAPI + r"""
int main(void){
    int fd = open_rdwr("/dev/capi20"); if (fd < 0) return 0;
    (void)ioctl(fd, CAPI_INSTALLED);
    close(fd);
    return 0;
}
""")

wr("capi_ioctl_manufacturer_cmd.c", COMMON_CAPI + r"""
int main(void){
    int fd = open_rdwr("/dev/capi20"); if (fd < 0) return 0;
    struct capi_manufacturer_cmd m; memset(&m, 0, sizeof(m));
    (void)ioctl(fd, CAPI_MANUFACTURER_CMD, &m);
    close(fd);
    return 0;
}
""")

for name, code in [
    ("capi_ioctl_set_flags.c", "CAPI_SET_FLAGS"),
    ("capi_ioctl_clr_flags.c", "CAPI_CLR_FLAGS"),
]:
    wr(name, COMMON_CAPI + f"""
int main(void){{
    int fd = open_rdwr("/dev/capi20"); if (fd < 0) return 0;
    int v = 1;
    (void)ioctl(fd, {code}, &v);
    close(fd);
    return 0;
}}
""")

wr("capi_ioctl_get_flags.c", COMMON_CAPI + r"""
int main(void){
    int fd = open_rdwr("/dev/capi20"); if (fd < 0) return 0;
    int v = 0;
    (void)ioctl(fd, CAPI_GET_FLAGS, &v);
    close(fd);
    return 0;
}
""")

for name, code in [
    ("capi_ioctl_ncci_opencount.c", "CAPI_NCCI_OPENCOUNT"),
    ("capi_ioctl_ncci_getunit.c", "CAPI_NCCI_GETUNIT"),
]:
    wr(name, COMMON_CAPI + f"""
int main(void){{
    int fd = open_rdwr("/dev/capi20"); if (fd < 0) return 0;
    int v = 0;
    (void)ioctl(fd, {code}, &v);
    close(fd);
    return 0;
}}
""")

wr("open_proc_capi20.c", COMMON + r"""
int main(void){
    int fd = open("/proc/capi/capi20", O_RDONLY|O_CLOEXEC);
    if (fd >= 0) close(fd);
    return 0;
}
""")

wr("open_proc_capi20ncci.c", COMMON + r"""
int main(void){
    int fd = open("/proc/capi/capi20ncci", O_RDONLY|O_CLOEXEC);
    if (fd >= 0) close(fd);
    return 0;
}
""")

wr("misdntimer_imaddtimer_0.c", COMMON + r"""
int main(void){
    int fd = open("/dev/mISDNtimer", O_RDWR|O_CLOEXEC);
    if (fd < 0) return 0;
    int v = 0;
    (void)ioctl(fd, IMADDTIMER, &v);
    close(fd);
    return 0;
}
""")

for t in [20, 50, 1000000, -1]:
    wr(f"misdntimer_imaddtimer_{t}.c", COMMON + f"""
int main(void){{
    int fd = open("/dev/mISDNtimer", O_RDWR|O_CLOEXEC);
    if (fd < 0) return 0;
    int v = {t};
    (void)ioctl(fd, IMADDTIMER, &v);
    close(fd);
    return 0;
}}
""")

for tid in [0,1,2,3]:
    wr(f"misdntimer_imdeltimer_{tid}.c", COMMON + f"""
int main(void){{
    int fd = open("/dev/mISDNtimer", O_RDWR|O_CLOEXEC);
    if (fd < 0) return 0;
    int v = {tid};
    (void)ioctl(fd, IMDELTIMER, &v);
    close(fd);
    return 0;
}}
""")