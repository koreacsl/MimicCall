import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_tipc"
os.makedirs(OUTDIR, exist_ok=True)

SOCK_TYPES = [
    ("dgram", "SOCK_DGRAM"),
    ("seqpacket", "SOCK_SEQPACKET"),
]

TIPC_SERVICE_TYPES = [
    "TIPC_NODE_STATE",
    "TIPC_TOP_SRV",
    "TIPC_LINK_STATE",
    "TIPC_SERVICE_TYPE0",
    "TIPC_SERVICE_TYPE1",
    "TIPC_SERVICE_TYPE2",
    "TIPC_SERVICE_TYPE3",
]

C_TEMPLATE = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/net.h>
#include <linux/socket.h>
#include <linux/tipc.h>

static int run_test(void) {
    int s = socket(AF_TIPC, SOCKTYPE | SOCK_CLOEXEC, 0);
    if (s < 0) return 0;

    struct sockaddr_tipc sa;
    memset(&sa, 0, sizeof(sa));
    sa.family = AF_TIPC;
    sa.addrtype = TIPC_ADDR_NAME;
    sa.scope = 0;
    sa.addr.name.name.type = SERVICE_TYPE;
    sa.addr.name.name.instance = 0;
    sa.addr.name.domain = 0;

    int v = 0, out = 0;
    socklen_t olen = sizeof(out);

    (void)setsockopt(s, SOL_TIPC, TIPC_IMPORTANCE, &v, sizeof(v));
    (void)setsockopt(s, SOL_TIPC, TIPC_SRC_DROPPABLE, &v, sizeof(v));
    (void)setsockopt(s, SOL_TIPC, TIPC_DEST_DROPPABLE, &v, sizeof(v));
    (void)setsockopt(s, SOL_TIPC, TIPC_CONN_TIMEOUT, &v, sizeof(v));

    (void)getsockopt(s, SOL_TIPC, TIPC_IMPORTANCE, &out, &olen);
    olen = sizeof(out);
    (void)getsockopt(s, SOL_TIPC, TIPC_SRC_DROPPABLE, &out, &olen);
    olen = sizeof(out);
    (void)getsockopt(s, SOL_TIPC, TIPC_DEST_DROPPABLE, &out, &olen);
    olen = sizeof(out);
    (void)getsockopt(s, SOL_TIPC, TIPC_CONN_TIMEOUT, &out, &olen);
    olen = sizeof(out);
    (void)getsockopt(s, SOL_TIPC, TIPC_NODE_RECVQ_DEPTH, &out, &olen);
    olen = sizeof(out);
    (void)getsockopt(s, SOL_TIPC, TIPC_SOCK_RECVQ_DEPTH, &out, &olen);

    struct iovec iov = { .iov_base = NULL, .iov_len = 0 };
    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    (void)sendmsg(s, &msg, MSG_DONTWAIT);

    close(s);
    return 0;
}

int main(void) { return run_test(); }
""").lstrip()

def write_test(sock_suffix, sock_macro, svc_macro):
    src = C_TEMPLATE.replace("SOCKTYPE", sock_macro).replace("SERVICE_TYPE", svc_macro)
    fname = f"tipc_{sock_suffix}_{svc_macro.lower()}.c"
    with open(os.path.join(OUTDIR, fname), "w") as f:
        f.write(src)

count = 0
for sock_suffix, sock_macro in SOCK_TYPES:
    for svc in TIPC_SERVICE_TYPES:
        write_test(sock_suffix, sock_macro, svc)
        count += 1