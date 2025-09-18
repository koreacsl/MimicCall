import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_tipc_netlink"
os.makedirs(OUTDIR, exist_ok=True)

NL_FLAGS_COMBOS = [
    ("noflag", "0"),
    ("req", "NLM_F_REQUEST"),
    ("ack", "NLM_F_ACK"),
    ("req_ack", "NLM_F_REQUEST|NLM_F_ACK"),
]

TIPC_CMDS = [
    "TIPC_CMD_SET_LINK_TOL",
    "TIPC_CMD_SET_LINK_PRI",
    "TIPC_CMD_SET_LINK_WINDOW",
    "TIPC_CMD_ENABLE_BEARER",
    "TIPC_CMD_GET_BEARER_NAMES",
    "TIPC_CMD_GET_MEDIA_NAMES",
    "TIPC_CMD_SHOW_PORTS",
    "TIPC_CMD_GET_REMOTE_MNG",
    "TIPC_CMD_GET_MAX_PORTS",
    "TIPC_CMD_GET_NETID",
    "TIPC_CMD_GET_NODES",
    "TIPC_CMD_GET_LINKS",
    "TIPC_CMD_SET_NODE_ADDR",
    "TIPC_CMD_SHOW_NAME_TABLE",
    "TIPC_CMD_SHOW_LINK_STATS",
    "TIPC_CMD_SHOW_STATS",
    "TIPC_CMD_DISABLE_BEARER",
    "TIPC_CMD_RESET_LINK_STATS",
    "TIPC_CMD_SET_NETID",
]

TIPC2_CMDS = [
    "TIPC_NL_BEARER_DISABLE",
    "TIPC_NL_BEARER_ENABLE",
    "TIPC_NL_BEARER_GET",
    "TIPC_NL_BEARER_ADD",
    "TIPC_NL_BEARER_SET",
    "TIPC_NL_SOCK_GET",
    "TIPC_NL_PUBL_GET",
    "TIPC_NL_LINK_GET",
    "TIPC_NL_LINK_SET",
    "TIPC_NL_LINK_RESET_STATS",
    "TIPC_NL_MEDIA_GET",
    "TIPC_NL_MEDIA_SET",
    "TIPC_NL_NODE_GET",
    "TIPC_NL_NET_GET",
    "TIPC_NL_NET_SET",
    "TIPC_NL_NAME_TABLE_GET",
    "TIPC_NL_MON_SET",
    "TIPC_NL_MON_GET",
    "TIPC_NL_MON_PEER_GET",
    "TIPC_NL_PEER_REMOVE",
    "TIPC_NL_UDP_GET_REMOTEIP",
    "TIPC_NL_KEY_SET",
    "TIPC_NL_KEY_FLUSH",
]

C_TEMPLATE = dedent(r"""
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>
#include <linux/socket.h>
#include <linux/net.h>

#include <linux/tipc_netlink.h>
#include <linux/tipc_config.h>
#include <linux/tipc_sockets_diag.h>

static int build_and_send(int nl_flags, int tipc_cmd, int tipc_v2)
{
    int s = socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_GENERIC);
    if (s < 0) return 0;

    struct {
        struct nlmsghdr nlh;
        struct genlmsghdr gnlh;
        char pad[4];
    } __attribute__((packed)) msg;

    memset(&msg, 0, sizeof(msg));

    msg.nlh.nlmsg_len = sizeof(msg);
    msg.nlh.nlmsg_type = 0;
    msg.nlh.nlmsg_flags = nl_flags;
    msg.nlh.nlmsg_seq = 1;
    msg.nlh.nlmsg_pid = (uint32_t)getpid();

    msg.gnlh.cmd = (uint8_t)(tipc_cmd & 0xff);
    msg.gnlh.version = 0;

    struct sockaddr_nl nladdr;
    memset(&nladdr, 0, sizeof(nladdr));
    nladdr.nl_family = AF_NETLINK;

    struct iovec iov = {
        .iov_base = &msg,
        .iov_len  = sizeof(msg),
    };

    struct msghdr msgh = {
        .msg_name = &nladdr,
        .msg_namelen = sizeof(nladdr),
        .msg_iov = &iov,
        .msg_iovlen = 1,
        .msg_control = NULL,
        .msg_controllen = 0,
        .msg_flags = 0,
    };

    (void)sendmsg(s, &msgh, MSG_DONTWAIT);
    close(s);
    return 0;
}

int main(void)
{
    return build_and_send(NL_FLAGS_VAL, CMD_VAL, IS_V2);
}
""").lstrip()

def write_test(name, nlflag_expr, cmd, is_v2):
    src = C_TEMPLATE
    src = src.replace("NL_FLAGS_VAL", nlflag_expr)
    src = src.replace("CMD_VAL", cmd)
    src = src.replace("IS_V2", "1" if is_v2 else "0")
    with open(os.path.join(OUTDIR, name), "w") as f:
        f.write(src)

count = 0

for cmd in TIPC_CMDS:
    for flag_suffix, nlflag_expr in NL_FLAGS_COMBOS:
        fname = f"tipc_{cmd.lower()}_{flag_suffix}.c"
        write_test(fname, nlflag_expr, cmd, False)
        count += 1

for cmd in TIPC2_CMDS:
    for flag_suffix, nlflag_expr in NL_FLAGS_COMBOS:
        fname = f"tipc2_{cmd.lower()}_{flag_suffix}.c"
        write_test(fname, nlflag_expr, cmd, True)
        count += 1