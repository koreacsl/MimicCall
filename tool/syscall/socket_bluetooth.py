import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_bluetooth"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <linux/socket.h>
#include <linux/net.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/l2cap.h>
#include <bluetooth/cmtp.h>
#include <bluetooth/bnep.h>
#include <bluetooth/hidp.h>
#include <bluetooth/sco.h>
#include <bluetooth/hci.h>
#include <bluetooth/rfcomm.h>
#include <asm/ioctls.h>

#ifndef SOL_BLUETOOTH
#define SOL_BLUETOOTH 274
#endif
#ifndef SOL_L2CAP
#define SOL_L2CAP 6
#endif
#ifndef SOL_RFCOMM
#define SOL_RFCOMM 18
#endif
#ifndef SOL_SCO
#define SOL_SCO 17
#endif

static int s_hci(void){ int s=socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI); if(s<0) return -1; return s; }
static int s_sco(void){ int s=socket(AF_BLUETOOTH, SOCK_SEQPACKET, BTPROTO_SCO); if(s<0) return -1; return s; }
static int s_l2(int t){ int s=socket(AF_BLUETOOTH, t, BTPROTO_L2CAP); if(s<0) return -1; return s; }
static int s_rf(int t){ int s=socket(AF_BLUETOOTH, t, BTPROTO_RFCOMM); if(s<0) return -1; return s; }
static int s_hidp(void){ int s=socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_HIDP); if(s<0) return -1; return s; }
static int s_cmtp(void){ int s=socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_CMTP); if(s<0) return -1; return s; }
static int s_bnep(void){ int s=socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_BNEP); if(s<0) return -1; return s; }

static void ba_any(bdaddr_t *a){ memset(a, 0, sizeof(*a)); }
static void sa_hci(struct sockaddr_hci *sa, int16_t dev, uint16_t chan){
    memset(sa,0,sizeof(*sa)); sa->hci_family=AF_BLUETOOTH; sa->hci_dev=dev; sa->hci_channel=chan;
}
static void sa_sco(struct sockaddr_sco *sa){
    memset(sa,0,sizeof(*sa)); sa->sco_family=AF_BLUETOOTH; ba_any(&sa->sco_bdaddr);
}
static void sa_l2(struct sockaddr_l2 *sa, uint8_t bdtype){
    memset(sa,0,sizeof(*sa)); sa->l2_family=AF_BLUETOOTH; sa->l2_psm=0; ba_any(&sa->l2_bdaddr); sa->l2_cid=0; sa->l2_bdaddr_type=bdtype;
}
static void sa_rc(struct sockaddr_rc *sa){
    memset(sa,0,sizeof(*sa)); sa->rc_family=AF_BLUETOOTH; ba_any(&sa->rc_bdaddr); sa->rc_channel=1;
}
""").lstrip()

HCI_BIND = COMMON + dedent(r"""
int main(void){
    int s=s_hci(); if(s<0) return 0;
    struct sockaddr_hci sa; sa_hci(&sa, -1, HCI_CHANNEL_RAW);
    (void)bind(s,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}
""")

HCI_SETSO_DATA_DIR = COMMON + dedent(r"""
int main(void){
    int s=s_hci(); if(s<0) return 0; int v=0;
    (void)setsockopt(s, 0, HCI_DATA_DIR, &v, sizeof(v));
    close(s); return 0;
}
""")

HCI_SETSO_TIME_STAMP = COMMON + dedent(r"""
int main(void){
    int s=s_hci(); if(s<0) return 0; int v=0;
    (void)setsockopt(s, 0, HCI_TIME_STAMP, &v, sizeof(v));
    close(s); return 0;
}
""")

HCI_SETSO_FILTER = COMMON + dedent(r"""
int main(void){
    int s=s_hci(); if(s<0) return 0;
    struct hci_ufilter f; memset(&f,0,sizeof(f));
    (void)setsockopt(s, 0, HCI_FILTER, &f, sizeof(f));
    close(s); return 0;
}
""")

HCI_GETSO_DATA_DIR = COMMON + dedent(r"""
int main(void){
    int s=s_hci(); if(s<0) return 0; int v=0; socklen_t l=sizeof(v);
    (void)getsockopt(s, 0, HCI_DATA_DIR, &v, &l);
    close(s); return 0;
}
""")

HCI_GETSO_TIME_STAMP = COMMON + dedent(r"""
int main(void){
    int s=s_hci(); if(s<0) return 0; int v=0; socklen_t l=sizeof(v);
    (void)getsockopt(s, 0, HCI_TIME_STAMP, &v, &l);
    close(s); return 0;
}
""")

HCI_GETSO_FILTER = COMMON + dedent(r"""
int main(void){
    int s=s_hci(); if(s<0) return 0; struct hci_ufilter f; socklen_t l=sizeof(f);
    (void)getsockopt(s, 0, HCI_FILTER, &f, &l);
    close(s); return 0;
}
""")

HCI_WRITE = COMMON + dedent(r"""
int main(void){
    int s=s_hci(); if(s<0) return 0;
    char b=0; (void)write(s,&b,1);
    close(s); return 0;
}
""")

with open(os.path.join(OUTDIR, "hci_bind.c"), "w") as f: f.write(HCI_BIND)
with open(os.path.join(OUTDIR, "hci_setsockopt_data_dir.c"), "w") as f: f.write(HCI_SETSO_DATA_DIR)
with open(os.path.join(OUTDIR, "hci_setsockopt_time_stamp.c"), "w") as f: f.write(HCI_SETSO_TIME_STAMP)
with open(os.path.join(OUTDIR, "hci_setsockopt_filter.c"), "w") as f: f.write(HCI_SETSO_FILTER)
with open(os.path.join(OUTDIR, "hci_getsockopt_data_dir.c"), "w") as f: f.write(HCI_GETSO_DATA_DIR)
with open(os.path.join(OUTDIR, "hci_getsockopt_time_stamp.c"), "w") as f: f.write(HCI_GETSO_TIME_STAMP)
with open(os.path.join(OUTDIR, "hci_getsockopt_filter.c"), "w") as f: f.write(HCI_GETSO_FILTER)
with open(os.path.join(OUTDIR, "hci_write.c"), "w") as f: f.write(HCI_WRITE)

hci_chans = ["HCI_CHANNEL_RAW","HCI_CHANNEL_USER","HCI_CHANNEL_MONITOR","HCI_CHANNEL_CONTROL","HCI_CHANNEL_LOGGING"]
for ch in hci_chans:
    code = f"""
{COMMON}
int main(void){{
    int s=s_hci(); if(s<0) return 0;
    struct sockaddr_hci sa; sa_hci(&sa, -1, {ch});
    (void)bind(s,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}}
"""
    with open(os.path.join(OUTDIR, f"hci_bind_chan_{ch.lower().replace('hci_channel_','')}.c"), "w") as f:
        f.write(code)

hci_ioctls = [
"HCIDEVUP","HCIDEVDOWN","HCIDEVRESET","HCIDEVRESTAT","HCIGETDEVLIST","HCIGETDEVINFO",
"HCIGETCONNLIST","HCIGETCONNINFO","HCIGETAUTHINFO","HCISETRAW","HCISETSCAN","HCISETAUTH",
"HCISETENCRYPT","HCISETPTYPE","HCISETLINKPOL","HCISETLINKMODE","HCISETACLMTU","HCISETSCOMTU",
"HCIBLOCKADDR","HCIUNBLOCKADDR"
]
for cmd in hci_ioctls:
    code = f"""
{COMMON}
int main(void){{
    int s=s_hci(); if(s<0) return 0;
    unsigned char buf[32]; memset(buf,0,sizeof(buf));
    (void)ioctl(s, {cmd}, buf);
    close(s); return 0;
}}
"""
    with open(os.path.join(OUTDIR, f"hci_ioctl_{cmd.lower()}.c"), "w") as f:
        f.write(code)

HCI_INQ = COMMON + dedent(r"""
int main(void){
    int s=s_hci(); if(s<0) return 0;
    struct hci_inquiry_req r; memset(&r,0,sizeof(r));
    (void)ioctl(s, HCIINQUIRY, &r);
    close(s); return 0;
}
""")
with open(os.path.join(OUTDIR, "hci_ioctl_hciinquiry.c"), "w") as f: f.write(HCI_INQ)

SCO_BIND   = COMMON + dedent(r"""
int main(void){
    int s=s_sco(); if(s<0) return 0;
    struct sockaddr_sco sa; sa_sco(&sa);
    (void)bind(s,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}
""")
SCO_CONNECT= COMMON + dedent(r"""
int main(void){
    int s=s_sco(); if(s<0) return 0;
    struct sockaddr_sco sa; sa_sco(&sa);
    (void)connect(s,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}
""")
SCO_GETOPT1= COMMON + dedent(r"""
int main(void){
    int s=s_sco(); if(s<0) return 0;
    unsigned char buf[16]; socklen_t l=sizeof(buf);
    (void)getsockopt(s, SOL_SCO, SCO_OPTIONS, buf, &l);
    close(s); return 0;
}
""")
SCO_GETOPT2= COMMON + dedent(r"""
int main(void){
    int s=s_sco(); if(s<0) return 0;
    unsigned char buf[16]; socklen_t l=sizeof(buf);
    (void)getsockopt(s, SOL_SCO, SCO_CONNINFO, buf, &l);
    close(s); return 0;
}
""")
with open(os.path.join(OUTDIR, "sco_bind.c"), "w") as f: f.write(SCO_BIND)
with open(os.path.join(OUTDIR, "sco_connect.c"), "w") as f: f.write(SCO_CONNECT)
with open(os.path.join(OUTDIR, "sco_get_options.c"), "w") as f: f.write(SCO_GETOPT1)
with open(os.path.join(OUTDIR, "sco_get_conninfo.c"), "w") as f: f.write(SCO_GETOPT2)

L2_BIND = COMMON + dedent(r"""
int main(void){
    int s=s_l2(SOCK_SEQPACKET); if(s<0) return 0;
    struct sockaddr_l2 sa; sa_l2(&sa, BDADDR_BREDR);
    (void)bind(s,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}
""")
L2_CONNECT = COMMON + dedent(r"""
int main(void){
    int s=s_l2(SOCK_SEQPACKET); if(s<0) return 0;
    struct sockaddr_l2 sa; sa_l2(&sa, BDADDR_BREDR);
    (void)connect(s,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}
""")
L2_ACCEPT4 = COMMON + dedent(r"""
#include <fcntl.h>
int main(void){
    int s=s_l2(SOCK_SEQPACKET); if(s<0) return 0;
    int c = accept4(s, NULL, NULL, 0);
    if(c>=0) close(c);
    close(s); return 0;
}
""")
with open(os.path.join(OUTDIR, "l2cap_bind.c"), "w") as f: f.write(L2_BIND)
with open(os.path.join(OUTDIR, "l2cap_connect.c"), "w") as f: f.write(L2_CONNECT)
with open(os.path.join(OUTDIR, "l2cap_accept4.c"), "w") as f: f.write(L2_ACCEPT4)

L2_SET_OPT = COMMON + dedent(r"""
int main(void){
    int s=s_l2(SOCK_SEQPACKET); if(s<0) return 0;
    struct l2cap_options o; memset(&o,0,sizeof(o));
    (void)setsockopt(s, SOL_L2CAP, L2CAP_OPTIONS, &o, sizeof(o));
    close(s); return 0;
}
""")
L2_GET_OPT = COMMON + dedent(r"""
int main(void){
    int s=s_l2(SOCK_SEQPACKET); if(s<0) return 0;
    struct l2cap_options o; socklen_t l=sizeof(o);
    (void)getsockopt(s, SOL_L2CAP, L2CAP_OPTIONS, &o, &l);
    close(s); return 0;
}
""")
L2_SET_CONNINFO = COMMON + dedent(r"""
int main(void){
    int s=s_l2(SOCK_SEQPACKET); if(s<0) return 0;
    struct l2cap_conninfo ci; memset(&ci,0,sizeof(ci));
    (void)setsockopt(s, SOL_L2CAP, L2CAP_CONNINFO, &ci, sizeof(ci));
    close(s); return 0;
}
""")
L2_GET_CONNINFO = COMMON + dedent(r"""
int main(void){
    int s=s_l2(SOCK_SEQPACKET); if(s<0) return 0;
    struct l2cap_conninfo ci; socklen_t l=sizeof(ci);
    (void)getsockopt(s, SOL_L2CAP, L2CAP_CONNINFO, &ci, &l);
    close(s); return 0;
}
""")
with open(os.path.join(OUTDIR, "l2cap_setsockopt_options.c"), "w") as f: f.write(L2_SET_OPT)
with open(os.path.join(OUTDIR, "l2cap_getsockopt_options.c"), "w") as f: f.write(L2_GET_OPT)
with open(os.path.join(OUTDIR, "l2cap_setsockopt_conninfo.c"), "w") as f: f.write(L2_SET_CONNINFO)
with open(os.path.join(OUTDIR, "l2cap_getsockopt_conninfo.c"), "w") as f: f.write(L2_GET_CONNINFO)

l2_types = ["SOCK_SEQPACKET","SOCK_STREAM","SOCK_DGRAM","SOCK_RAW"]
for t in l2_types:
    code = f"""
{COMMON}
int main(void){{
    int s=s_l2({t}); if(s<0) return 0;
    close(s); return 0;
}}
"""
    with open(os.path.join(OUTDIR, f"l2cap_socket_type_{t.lower().replace('sock_','')}.c"), "w") as f:
        f.write(code)

l2_lm_flags = ["L2CAP_LM_MASTER","L2CAP_LM_AUTH","L2CAP_LM_ENCRYPT","L2CAP_LM_TRUSTED","L2CAP_LM_RELIABLE","L2CAP_LM_SECURE","L2CAP_LM_FIPS"]
for fl in l2_lm_flags:
    code = f"""
{COMMON}
int main(void){{
    int s=s_l2(SOCK_SEQPACKET); if(s<0) return 0;
    int v = {fl};
    (void)setsockopt(s, SOL_L2CAP, L2CAP_LM, &v, sizeof(v));
    close(s); return 0;
}}
"""
    with open(os.path.join(OUTDIR, f"l2cap_lm_set_{fl.lower().replace('l2cap_lm_','')}.c"), "w") as f:
        f.write(code)

bd_types = ["BDADDR_BREDR","BDADDR_LE_PUBLIC","BDADDR_LE_RANDOM"]
for bt in bd_types:
    code = f"""
{COMMON}
int main(void){{
    int s=s_l2(SOCK_SEQPACKET); if(s<0) return 0;
    struct sockaddr_l2 sa; sa_l2(&sa, {bt});
    (void)bind(s,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}}
"""
    with open(os.path.join(OUTDIR, f"l2cap_bind_bdaddr_type_{bt.lower().replace('bdaddr_','')}.c"), "w") as f:
        f.write(code)

rf_types = ["SOCK_STREAM","SOCK_RAW"]
for t in rf_types:
    code = f"""
{COMMON}
int main(void){{
    int s=s_rf({t}); if(s<0) return 0;
    close(s); return 0;
}}
"""
    with open(os.path.join(OUTDIR, f"rfcomm_socket_type_{t.lower().replace('sock_','')}.c"), "w") as f:
        f.write(code)

RFCOMM_BIND = COMMON + dedent(r"""
int main(void){
    int s=s_rf(SOCK_STREAM); if(s<0) return 0;
    struct sockaddr_rc sa; sa_rc(&sa);
    (void)bind(s,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}
""")
RFCOMM_CONNECT = COMMON + dedent(r"""
int main(void){
    int s=s_rf(SOCK_STREAM); if(s<0) return 0;
    struct sockaddr_rc sa; sa_rc(&sa);
    (void)connect(s,(struct sockaddr*)&sa,sizeof(sa));
    close(s); return 0;
}
""")
with open(os.path.join(OUTDIR, "rfcomm_bind.c"), "w") as f: f.write(RFCOMM_BIND)
with open(os.path.join(OUTDIR, "rfcomm_connect.c"), "w") as f: f.write(RFCOMM_CONNECT)

for fl in l2_lm_flags:
    code = f"""
{COMMON}
int main(void){{
    int s=s_rf(SOCK_STREAM); if(s<0) return 0;
    int v={fl};
    (void)setsockopt(s, SOL_RFCOMM, RFCOMM_LM, &v, sizeof(v));
    close(s); return 0;
}}
"""
    with open(os.path.join(OUTDIR, f"rfcomm_lm_set_{fl.lower().replace('l2cap_lm_','')}.c"), "w") as f:
        f.write(code)

hidp_ios = [
("HIDPCONNADD", "struct hidp_connadd_req r; memset(&r,0,sizeof(r)); (void)ioctl(s, HIDPCONNADD, &r);"),
("HIDPCONNDEL", "struct hidp_conndel_req r; memset(&r,0,sizeof(r)); (void)ioctl(s, HIDPCONNDEL, &r);"),
("HIDPGETCONNLIST", "struct hidp_connlist_req r; memset(&r,0,sizeof(r)); (void)ioctl(s, HIDPGETCONNLIST, &r);"),
("HIDPGETCONNINFO", "struct hidp_conninfo r; memset(&r,0,sizeof(r)); (void)ioctl(s, HIDPGETCONNINFO, &r);"),
]
for name, body in hidp_ios:
    code = f"""
{COMMON}
int main(void){{
    int s=s_hidp(); if(s<0) return 0;
    {body}
    close(s); return 0;
}}
"""
    with open(os.path.join(OUTDIR, f"hidp_ioctl_{name.lower()}.c"), "w") as f:
        f.write(code)

cmtp_ios = [
("CMTPCONNADD", "struct cmtp_connadd_req r; memset(&r,0,sizeof(r)); (void)ioctl(s, CMTPCONNADD, &r);"),
("CMTPCONNDEL", "struct cmtp_conndel_req r; memset(&r,0,sizeof(r)); (void)ioctl(s, CMTPCONNDEL, &r);"),
("CMTPGETCONNLIST", "struct cmtp_connlist_req r; memset(&r,0,sizeof(r)); (void)ioctl(s, CMTPGETCONNLIST, &r);"),
("CMTPGETCONNINFO", "struct cmtp_conninfo r; memset(&r,0,sizeof(r)); (void)ioctl(s, CMTPGETCONNINFO, &r);"),
]
for name, body in cmtp_ios:
    code = f"""
{COMMON}
int main(void){{
    int s=s_cmtp(); if(s<0) return 0;
    {body}
    close(s); return 0;
}}
"""
    with open(os.path.join(OUTDIR, f"cmtp_ioctl_{name.lower()}.c"), "w") as f:
        f.write(code)

bnep_ios = [
("BNEPCONNADD", "struct bnep_connadd_req r; memset(&r,0,sizeof(r)); (void)ioctl(s, BNEPCONNADD, &r);"),
("BNEPCONNDEL", "struct bnep_conndel_req r; memset(&r,0,sizeof(r)); (void)ioctl(s, BNEPCONNDEL, &r);"),
("BNEPGETCONNLIST", "struct bnep_connlist_req r; memset(&r,0,sizeof(r)); (void)ioctl(s, BNEPGETCONNLIST, &r);"),
("BNEPGETCONNINFO", "struct bnep_conninfo r; memset(&r,0,sizeof(r)); (void)ioctl(s, BNEPGETCONNINFO, &r);"),
("BNEPGETSUPPFEAT", "int v=0; (void)ioctl(s, BNEPGETSUPPFEAT, &v);"),
]
for name, body in bnep_ios:
    code = f"""
{COMMON}
int main(void){{
    int s=s_bnep(); if(s<0) return 0;
    {body}
    close(s); return 0;
}}
"""
    with open(os.path.join(OUTDIR, f"bnep_ioctl_{name.lower()}.c"), "w") as f:
        f.write(code)

BT_SECURITY_SET = COMMON + dedent(r"""
int main(void){
    int s=s_hci(); if(s<0) return 0;
    struct bt_security sec; memset(&sec,0,sizeof(sec));
    (void)setsockopt(s, SOL_BLUETOOTH, BT_SECURITY, &sec, sizeof(sec));
    close(s); return 0;
}
""")
BT_SECURITY_GET = COMMON + dedent(r"""
int main(void){
    int s=s_hci(); if(s<0) return 0;
    struct bt_security sec; socklen_t l=sizeof(sec);
    (void)getsockopt(s, SOL_BLUETOOTH, BT_SECURITY, &sec, &l);
    close(s); return 0;
}
""")
with open(os.path.join(OUTDIR, "bt_security_set.c"), "w") as f: f.write(BT_SECURITY_SET)
with open(os.path.join(OUTDIR, "bt_security_get.c"), "w") as f: f.write(BT_SECURITY_GET)

BT_DEFER_SETUP_SET = COMMON + dedent(r"""
int main(void){
    int s=s_hci(); if(s<0) return 0; int v=0;
    (void)setsockopt(s, SOL_BLUETOOTH, BT_DEFER_SETUP, &v, sizeof(v));
    close(s); return 0;
}
""")
BT_DEFER_SETUP_GET = COMMON + dedent(r"""
int main(void){
    int s=s_hci(); if(s<0) return 0; int v=0; socklen_t l=sizeof(v);
    (void)getsockopt(s, SOL_BLUETOOTH, BT_DEFER_SETUP, &v, &l);
    close(s); return 0;
}
""")
with open(os.path.join(OUTDIR, "bt_defer_setup_set.c"), "w") as f: f.write(BT_DEFER_SETUP_SET)
with open(os.path.join(OUTDIR, "bt_defer_setup_get.c"), "w") as f: f.write(BT_DEFER_SETUP_GET)

voice_flags = ["BT_VOICE_TRANSPARENT","BT_VOICE_CVSD_16BIT"]
for fl in voice_flags:
    code = f"""
{COMMON}
int main(void){{
    int s=s_hci(); if(s<0) return 0;
    uint16_t v = {fl};
    (void)setsockopt(s, SOL_BLUETOOTH, BT_VOICE, &v, sizeof(v));
    close(s); return 0;
}}
"""
    with open(os.path.join(OUTDIR, f"bt_voice_set_{fl.lower().replace('bt_voice_','')}.c"), "w") as f:
        f.write(code)

misc_opts = [
    ("BT_FLUSHABLE", "int"),
    ("BT_POWER", "char"),
    ("BT_CHANNEL_POLICY", "int"),
    ("BT_SNDMTU", "short"),
    ("BT_RCVMTU", "short"),
]
for name, ctype in misc_opts:
    set_code = f"""
{COMMON}
int main(void){{
    int s=s_hci(); if(s<0) return 0;
    {ctype} v=0;
    (void)setsockopt(s, SOL_BLUETOOTH, {name}, &v, sizeof(v));
    close(s); return 0;
}}
"""
    get_code = f"""
{COMMON}
int main(void){{
    int s=s_hci(); if(s<0) return 0;
    {ctype} v=0; socklen_t l=sizeof(v);
    (void)getsockopt(s, SOL_BLUETOOTH, {name}, &v, &l);
    close(s); return 0;
}}
"""
    with open(os.path.join(OUTDIR, f"bt_{name.lower()}_set.c"), "w") as f: f.write(set_code)
    with open(os.path.join(OUTDIR, f"bt_{name.lower()}_get.c"), "w") as f: f.write(get_code)

SYSFS_ENABLE_0 = COMMON + dedent(r"""
#include <fcntl.h>
int main(void){
    int fd = open("/sys/kernel/debug/bluetooth/6lowpan_enable", O_RDWR);
    if (fd>=0){ const char s[]="0"; (void)write(fd,s,sizeof(s)-1); close(fd); }
    return 0;
}
""")
SYSFS_ENABLE_1 = COMMON + dedent(r"""
#include <fcntl.h>
int main(void){
    int fd = open("/sys/kernel/debug/bluetooth/6lowpan_enable", O_RDWR);
    if (fd>=0){ const char s[]="1"; (void)write(fd,s,sizeof(s)-1); close(fd); }
    return 0;
}
""")
with open(os.path.join(OUTDIR, "lowpan_enable_0.c"), "w") as f: f.write(SYSFS_ENABLE_0)
with open(os.path.join(OUTDIR, "lowpan_enable_1.c"), "w") as f: f.write(SYSFS_ENABLE_1)

control_cmds = [
"connect aa:aa:aa:aa:aa:10 0",
"connect aa:aa:aa:aa:aa:10 1",
"connect aa:aa:aa:aa:aa:10 2",
"connect aa:aa:aa:aa:aa:11 0",
"connect aa:aa:aa:aa:aa:11 1",
"connect aa:aa:aa:aa:aa:11 2",
"disconnect aa:aa:aa:aa:aa:10 0",
"disconnect aa:aa:aa:aa:aa:10 1",
"disconnect aa:aa:aa:aa:aa:10 2",
"disconnect aa:aa:aa:aa:aa:11 0",
"disconnect aa:aa:aa:aa:aa:11 1",
"disconnect aa:aa:aa:aa:aa:11 2",
]
for i, cmd in enumerate(control_cmds):
    code = f"""
{COMMON}
#include <fcntl.h>
int main(void){{
    int fd = open("/sys/kernel/debug/bluetooth/6lowpan_control", O_RDWR);
    if(fd>=0){{ const char s[]="{cmd}"; (void)write(fd,s,sizeof(s)-1); close(fd); }}
    return 0;
}}
"""
    with open(os.path.join(OUTDIR, f"lowpan_control_{i:02d}.c"), "w") as f:
        f.write(code)