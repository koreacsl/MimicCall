import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/netfilter_ipvs"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <linux/socket.h>
#include <linux/fcntl.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>
#include <linux/ip_vs.h>

#ifndef SOL_IP
#define SOL_IP 0
#endif

#ifndef NETLINK_GENERIC
#define NETLINK_GENERIC 16
#endif

static int ms_ip(void){ int s = socket(AF_INET, SOCK_DGRAM, 0); if(s<0) return -1; return s; }
static int ms_genl(void){ int s = socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC); if(s<0) return -1; return s; }
""").lstrip()

SET_ADD = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    struct ip_vs_service_user su; memset(&su, 0, sizeof(su));
    (void)setsockopt(s, SOL_IP, IP_VS_SO_SET_ADD, &su, sizeof(su));
    close(s); return 0;
}
""")

SET_EDIT = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    struct ip_vs_service_user su; memset(&su, 0, sizeof(su));
    (void)setsockopt(s, SOL_IP, IP_VS_SO_SET_EDIT, &su, sizeof(su));
    close(s); return 0;
}
""")

SET_DEL = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    struct ip_vs_service_user su; memset(&su, 0, sizeof(su));
    (void)setsockopt(s, SOL_IP, IP_VS_SO_SET_DEL, &su, sizeof(su));
    close(s); return 0;
}
""")

SET_FLUSH = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    (void)setsockopt(s, SOL_IP, IP_VS_SO_SET_FLUSH, NULL, 0);
    close(s); return 0;
}
""")

SET_ADDDEST = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    struct ip_vs_svcdest_user sd; memset(&sd, 0, sizeof(sd));
    (void)setsockopt(s, SOL_IP, IP_VS_SO_SET_ADDDEST, &sd, sizeof(sd));
    close(s); return 0;
}
""")

SET_DELDEST = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    struct ip_vs_svcdest_user sd; memset(&sd, 0, sizeof(sd));
    (void)setsockopt(s, SOL_IP, IP_VS_SO_SET_DELDEST, &sd, sizeof(sd));
    close(s); return 0;
}
""")

SET_EDITDEST = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    struct ip_vs_svcdest_user sd; memset(&sd, 0, sizeof(sd));
    (void)setsockopt(s, SOL_IP, IP_VS_SO_SET_EDITDEST, &sd, sizeof(sd));
    close(s); return 0;
}
""")

SET_TIMEOUT = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    struct ip_vs_timeout_user tu; memset(&tu, 0, sizeof(tu));
    (void)setsockopt(s, SOL_IP, IP_VS_SO_SET_TIMEOUT, &tu, sizeof(tu));
    close(s); return 0;
}
""")

SET_STARTDAEMON = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    struct ip_vs_daemon_user du; memset(&du, 0, sizeof(du));
    (void)setsockopt(s, SOL_IP, IP_VS_SO_SET_STARTDAEMON, &du, sizeof(du));
    close(s); return 0;
}
""")

SET_STOPDAEMON = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    struct ip_vs_daemon_user du; memset(&du, 0, sizeof(du));
    (void)setsockopt(s, SOL_IP, IP_VS_SO_SET_STOPDAEMON, &du, sizeof(du));
    close(s); return 0;
}
""")

SET_ZERO = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    struct ip_vs_service_user su; memset(&su, 0, sizeof(su));
    (void)setsockopt(s, SOL_IP, IP_VS_SO_SET_ZERO, &su, sizeof(su));
    close(s); return 0;
}
""")

with open(os.path.join(OUTDIR, "set_add.c"), "w") as f: f.write(SET_ADD)
with open(os.path.join(OUTDIR, "set_edit.c"), "w") as f: f.write(SET_EDIT)
with open(os.path.join(OUTDIR, "set_del.c"), "w") as f: f.write(SET_DEL)
with open(os.path.join(OUTDIR, "set_flush.c"), "w") as f: f.write(SET_FLUSH)
with open(os.path.join(OUTDIR, "set_adddest.c"), "w") as f: f.write(SET_ADDDEST)
with open(os.path.join(OUTDIR, "set_deldest.c"), "w") as f: f.write(SET_DELDEST)
with open(os.path.join(OUTDIR, "set_editdest.c"), "w") as f: f.write(SET_EDITDEST)
with open(os.path.join(OUTDIR, "set_timeout.c"), "w") as f: f.write(SET_TIMEOUT)
with open(os.path.join(OUTDIR, "set_startdaemon.c"), "w") as f: f.write(SET_STARTDAEMON)
with open(os.path.join(OUTDIR, "set_stopdaemon.c"), "w") as f: f.write(SET_STOPDAEMON)
with open(os.path.join(OUTDIR, "set_zero.c"), "w") as f: f.write(SET_ZERO)

GET_VERSION = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    char buf[64]; socklen_t l = sizeof(buf);
    (void)getsockopt(s, SOL_IP, IP_VS_SO_GET_VERSION, buf, &l);
    close(s); return 0;
}
""")

GET_INFO = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    char buf[sizeof(struct ip_vs_getinfo)]; socklen_t l = sizeof(buf);
    (void)getsockopt(s, SOL_IP, IP_VS_SO_GET_INFO, buf, &l);
    close(s); return 0;
}
""")

GET_SERVICES = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    unsigned char buf[64]; socklen_t l = sizeof(buf);
    (void)getsockopt(s, SOL_IP, IP_VS_SO_GET_SERVICES, buf, &l);
    close(s); return 0;
}
""")

GET_SERVICE = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    unsigned char buf[sizeof(struct ip_vs_service_entry)]; socklen_t l = sizeof(buf);
    (void)getsockopt(s, SOL_IP, IP_VS_SO_GET_SERVICE, buf, &l);
    close(s); return 0;
}
""")

GET_DESTS = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    unsigned char buf[64]; socklen_t l = sizeof(buf);
    (void)getsockopt(s, SOL_IP, IP_VS_SO_GET_DESTS, buf, &l);
    close(s); return 0;
}
""")

GET_TIMEOUT = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    unsigned char buf[sizeof(struct ip_vs_timeout_user)]; socklen_t l = sizeof(buf);
    (void)getsockopt(s, SOL_IP, IP_VS_SO_GET_TIMEOUT, buf, &l);
    close(s); return 0;
}
""")

GET_DAEMON = COMMON + dedent(r"""
int main(void){
    int s = ms_ip(); if(s<0) return 0;
    unsigned char buf[2*sizeof(struct ip_vs_daemon_user)]; socklen_t l = sizeof(buf);
    (void)getsockopt(s, SOL_IP, IP_VS_SO_GET_DAEMON, buf, &l);
    close(s); return 0;
}
""")

with open(os.path.join(OUTDIR, "get_version.c"), "w") as f: f.write(GET_VERSION)
with open(os.path.join(OUTDIR, "get_info.c"), "w") as f: f.write(GET_INFO)
with open(os.path.join(OUTDIR, "get_services.c"), "w") as f: f.write(GET_SERVICES)
with open(os.path.join(OUTDIR, "get_service.c"), "w") as f: f.write(GET_SERVICE)
with open(os.path.join(OUTDIR, "get_dests.c"), "w") as f: f.write(GET_DESTS)
with open(os.path.join(OUTDIR, "get_timeout.c"), "w") as f: f.write(GET_TIMEOUT)
with open(os.path.join(OUTDIR, "get_daemon.c"), "w") as f: f.write(GET_DAEMON)

def genl_send_tpl(cmd_macro: str) -> str:
    return COMMON + f"""
int main(void){{
    int s = ms_genl(); if(s<0) return 0;
    char buf[NLMSG_SPACE(sizeof(struct genlmsghdr))];
    memset(buf, 0, sizeof(buf));
    struct nlmsghdr *nlh = (struct nlmsghdr*)buf;
    nlh->nlmsg_len = NLMSG_LENGTH(sizeof(struct genlmsghdr));
    nlh->nlmsg_type = 0;
    nlh->nlmsg_flags = 0;
    struct msghdr msg; memset(&msg,0,sizeof(msg));
    struct iovec iov; iov.iov_base = buf; iov.iov_len = nlh->nlmsg_len;
    msg.msg_iov = &iov; msg.msg_iovlen = 1;
    (void){cmd_macro};
    (void)sendmsg(s, &msg, 0);
    close(s); return 0;
}}
"""

genl_cmds = [
    ("IPVS_CMD_NEW_SERVICE", "sendmsg_cmd_new_service.c"),
    ("IPVS_CMD_SET_SERVICE", "sendmsg_cmd_set_service.c"),
    ("IPVS_CMD_DEL_SERVICE", "sendmsg_cmd_del_service.c"),
    ("IPVS_CMD_GET_SERVICE", "sendmsg_cmd_get_service.c"),
    ("IPVS_CMD_NEW_DEST", "sendmsg_cmd_new_dest.c"),
    ("IPVS_CMD_SET_DEST", "sendmsg_cmd_set_dest.c"),
    ("IPVS_CMD_DEL_DEST", "sendmsg_cmd_del_dest.c"),
    ("IPVS_CMD_GET_DEST", "sendmsg_cmd_get_dest.c"),
    ("IPVS_CMD_NEW_DAEMON", "sendmsg_cmd_new_daemon.c"),
    ("IPVS_CMD_DEL_DAEMON", "sendmsg_cmd_del_daemon.c"),
    ("IPVS_CMD_GET_DAEMON", "sendmsg_cmd_get_daemon.c"),
    ("IPVS_CMD_SET_CONFIG", "sendmsg_cmd_set_config.c"),
    ("IPVS_CMD_GET_CONFIG", "sendmsg_cmd_get_config.c"),
    ("IPVS_CMD_SET_INFO", "sendmsg_cmd_set_info.c"),
    ("IPVS_CMD_GET_INFO", "sendmsg_cmd_get_info.c"),
    ("IPVS_CMD_ZERO", "sendmsg_cmd_zero.c"),
    ("IPVS_CMD_FLUSH", "sendmsg_cmd_flush.c"),
]

for macro, fname in genl_cmds:
    with open(os.path.join(OUTDIR, fname), "w") as f:
        f.write(genl_send_tpl(macro))

PROC_FILES = [
"/proc/sys/net/ipv4/vs/sync_qlen_max",
"/proc/sys/net/ipv4/vs/sync_refresh_period",
"/proc/sys/net/ipv4/vs/sync_retries",
"/proc/sys/net/ipv4/vs/sync_sock_size",
"/proc/sys/net/ipv4/vs/sync_threshold",
"/proc/sys/net/ipv4/vs/sync_version",
"/proc/sys/net/ipv4/vs/am_droprate",
"/proc/sys/net/ipv4/vs/amemthresh",
"/proc/sys/net/ipv4/vs/backup_only",
"/proc/sys/net/ipv4/vs/cache_bypass",
"/proc/sys/net/ipv4/vs/conn_reuse_mode",
"/proc/sys/net/ipv4/vs/conntrack",
"/proc/sys/net/ipv4/vs/drop_entry",
"/proc/sys/net/ipv4/vs/drop_packet",
"/proc/sys/net/ipv4/vs/expire_nodest_conn",
"/proc/sys/net/ipv4/vs/expire_quiescent_template",
"/proc/sys/net/ipv4/vs/ignore_tunneled",
"/proc/sys/net/ipv4/vs/lblc_expiration",
"/proc/sys/net/ipv4/vs/lblcr_expiration",
"/proc/sys/net/ipv4/vs/nat_icmp_send",
"/proc/sys/net/ipv4/vs/pmtu_disc",
"/proc/sys/net/ipv4/vs/schedule_icmp",
"/proc/sys/net/ipv4/vs/secure_tcp",
"/proc/sys/net/ipv4/vs/sloppy_sctp",
"/proc/sys/net/ipv4/vs/sloppy_tcp",
"/proc/sys/net/ipv4/vs/snat_reroute",
"/proc/sys/net/ipv4/vs/sync_persist_mode",
"/proc/sys/net/ipv4/vs/sync_ports",
]

OPEN_TPL = COMMON + r"""
#include <fcntl.h>
int main(void){
    (void)openat(AT_FDCWD, "%s", O_RDWR, 0);
    return 0;
}
"""

for p in PROC_FILES:
    base = os.path.basename(p).replace('-', '_')
    with open(os.path.join(OUTDIR, f"open_{base}.c"), "w") as f:
        f.write(OPEN_TPL % p)

def write_flag(basename: str, body: str):
    with open(os.path.join(OUTDIR, basename), "w") as f:
        f.write(COMMON + body)

svc_flags = ["IP_VS_SVC_F_PERSISTENT","IP_VS_SVC_F_HASHED","IP_VS_SVC_F_ONEPACKET","IP_VS_SVC_F_SCHED1","IP_VS_SVC_F_SCHED2","IP_VS_SVC_F_SCHED3"]
for fl in svc_flags:
    body = f"""
int main(void){{
    int s=ms_ip(); if(s<0) return 0;
    struct ip_vs_service_user su; memset(&su,0,sizeof(su));
    su.flags.flags = {fl};
    struct ip_vs_getinfo gi; (void)gi;
    close(s); return 0;
}}
"""
    write_flag(f"flag_service_{fl.lower().replace('ip_vs_svc_f_','')}.c", body)

dest_flags = ["IP_VS_CONN_F_MASQ","IP_VS_CONN_F_LOCALNODE","IP_VS_CONN_F_TUNNEL","IP_VS_CONN_F_DROUTE","IP_VS_CONN_F_BYPASS","IP_VS_CONN_F_ONE_PACKET","IP_VS_CONN_F_NFCT"]
for fl in dest_flags:
    body = f"""
int main(void){{
    int s=ms_ip(); if(s<0) return 0;
    struct ip_vs_dest_user du; memset(&du,0,sizeof(du));
    du.conn_flags = {fl};
    char buf[64]; socklen_t l=sizeof(buf);
    (void)getsockopt(s,SOL_IP,IP_VS_SO_GET_VERSION,buf,&l);
    close(s); return 0;
}}
"""
    write_flag(f"flag_dest_{fl.lower().replace('ip_vs_conn_f_','')}.c", body)

daemon_states = ["IP_VS_STATE_NONE","IP_VS_STATE_MASTER","IP_VS_STATE_BACKUP"]
for fl in daemon_states:
    body = f"""
int main(void){{
    int s=ms_ip(); if(s<0) return 0;
    struct ip_vs_daemon_user du; memset(&du,0,sizeof(du));
    du.state = {fl};
    char buf[64]; socklen_t l=sizeof(buf);
    (void)getsockopt(s,SOL_IP,IP_VS_SO_GET_VERSION,buf,&l);
    close(s); return 0;
}}
"""
    write_flag(f"flag_daemon_{fl.lower().replace('ip_vs_state_','')}.c", body)

af_flags = ["AF_INET","AF_INET6"]
for fl in af_flags:
    body = f"""
int main(void){{
    int s=ms_ip(); if(s<0) return 0;
    struct ip_vs_service_user su; memset(&su,0,sizeof(su));
    (void){fl};
    char buf[64]; socklen_t l=sizeof(buf);
    (void)getsockopt(s,SOL_IP,IP_VS_SO_GET_VERSION,buf,&l);
    close(s); return 0;
}}
"""
    write_flag(f"flag_af_{fl.lower().replace('af_','')}.c", body)

tun_types = ["IP_VS_CONN_F_TUNNEL_TYPE_IPIP","IP_VS_CONN_F_TUNNEL_TYPE_GUE"]
for fl in tun_types:
    body = f"""
int main(void){{
    int s=ms_ip(); if(s<0) return 0;
    int v = {fl}; (void)v;
    char buf[64]; socklen_t l=sizeof(buf);
    (void)getsockopt(s,SOL_IP,IP_VS_SO_GET_VERSION,buf,&l);
    close(s); return 0;
}}
"""
    write_flag(f"flag_tun_{fl.lower().replace('ip_vs_conn_f_tunnel_type_','')}.c", body)

sched_names = ["none","dh","fo","lblc","lblcr","lc","nq","ovf","rr","sed","sh","wlc","wrr"]
for name in sched_names:
    body = f"""
int main(void){{
    int s=ms_ip(); if(s<0) return 0;
    struct ip_vs_service_user su; memset(&su,0,sizeof(su));
    strncpy(su.sched_name, "{name}", sizeof(su.sched_name)-1);
    char buf[64]; socklen_t l=sizeof(buf);
    (void)getsockopt(s,SOL_IP,IP_VS_SO_GET_VERSION,buf,&l);
    close(s); return 0;
}}
"""
    write_flag(f"param_sched_{name}.c", body)

genl_attr_single = [
    ("svc_af_inet.c", "IPVS_SVC_ATTR_AF", "AF_INET"),
    ("svc_af_inet6.c", "IPVS_SVC_ATTR_AF", "AF_INET6"),
]
for fname, attr, val in genl_attr_single:
    body = f"""
int main(void){{
    int s = ms_genl(); if(s<0) return 0;
    int a = {val}; (void)a; (void){attr};
    char b[32]; struct msghdr msg; memset(&msg,0,sizeof(msg));
    struct iovec iov; iov.iov_base=b; iov.iov_len=0; msg.msg_iov=&iov; msg.msg_iovlen=1;
    (void)sendmsg(s,&msg,0);
    close(s); return 0;
}}
"""
    write_flag(fname, body)