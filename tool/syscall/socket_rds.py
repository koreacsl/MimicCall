import os
from itertools import chain, combinations
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_rds"
os.makedirs(OUTDIR, exist_ok=True)

TRANSPORTS = ["RDS_TRANS_IB", "RDS_TRANS_IWARP", "RDS_TRANS_TCP", "RDS_TRANS_NONE"]

RDMA_FLAGS = ["RDS_RDMA_READWRITE", "RDS_RDMA_FENCE", "RDS_RDMA_INVALIDATE", "RDS_RDMA_USE_ONCE", "RDS_RDMA_DONTWAIT", "RDS_RDMA_NOTIFY_ME", "RDS_RDMA_SILENT"]

def all_combinations(flags):
    return chain.from_iterable(combinations(flags, r) for r in range(len(flags)+1))

C_TEMPLATE = dedent(r"""
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/uio.h>
#include <arpa/inet.h>

#include <linux/socket.h>
#include <linux/net.h>
#include <linux/in6.h>
#include <linux/rds.h>

static int s_rds(void){ return socket(AF_RDS, SOCK_SEQPACKET, 0); }

static void inaddr_any(struct sockaddr_in* sa){
    memset(sa, 0, sizeof(*sa));
    sa->sin_family = AF_INET;
    sa->sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    sa->sin_port = htons(0);
}

static void soset_blob(int s, int opt, const void* p, socklen_t l){
    (void)setsockopt(s, SOL_RDS, opt, p, l);
}

int main(void){
    int s = s_rds();
    if (s < 0) return 0;

    struct sockaddr_in sa;
    inaddr_any(&sa);
    (void)bind(s, (struct sockaddr*)&sa, sizeof(sa));
    (void)connect(s, (struct sockaddr*)&sa, sizeof(sa));

    int transport = TRANSPORTFLAG;
    soset_blob(s, SO_RDS_TRANSPORT, &transport, sizeof(transport));

    struct rds_get_mr_args getmr;
    memset(&getmr, 0, sizeof(getmr));
    getmr.flags = RDFLAGSMASK;
    soset_blob(s, RDS_GET_MR, &getmr, sizeof(getmr));

    close(s);
    return 0;
}
""").lstrip()

for t in TRANSPORTS:
    src = C_TEMPLATE.replace("TRANSPORTFLAG", t).replace("RDFLAGSMASK", "0")
    fname = f"rds_transport_{t.lower()}.c"
    with open(os.path.join(OUTDIR, fname), "w") as f:
        f.write(src)

for combo in all_combinations(RDMA_FLAGS):
    if not combo:
        mask_expr = "0"
        name = "none"
    else:
        mask_expr = " | ".join(combo)
        name = "_".join(flag.replace("RDS_RDMA_", "").lower() for flag in combo)
    src = C_TEMPLATE.replace("TRANSPORTFLAG", "RDS_TRANS_TCP").replace("RDFLAGSMASK", mask_expr)
    fname = f"rds_rdma_flags_{name}.c"
    with open(os.path.join(OUTDIR, fname), "w") as f:
        f.write(src)