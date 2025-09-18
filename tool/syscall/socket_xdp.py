import os
from textwrap import dedent
from itertools import product

OUTDIR = "./tool/cfiles/socket_xdp"
os.makedirs(OUTDIR, exist_ok=True)

sxdp_bits = [
    ("XDP_SHARED_UMEM", 1 << 0),
    ("XDP_COPY", 1 << 1),
    ("XDP_ZEROCOPY", 1 << 2),
    ("XDP_USE_NEED_WAKEUP", 1 << 3),
]

def combo_name(bits, mask):
    if mask == 0:
        return "none"
    names = [n for i,(n,_) in enumerate(bits) if mask & bits[i][1]]
    return "_".join(n.lower() for n in names)

sxdp_combos = []
for m in range(1 << len(sxdp_bits)):
    val_parts = []
    for i,(n,_) in enumerate(sxdp_bits):
        if m & (1 << i):
            val_parts.append(n)
    val_str = " | ".join(val_parts) if val_parts else "0"
    sxdp_combos.append( (combo_name(sxdp_bits, m), val_str) )

BIND_SXDP_TMPL = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <linux/net.h>
#include <linux/socket.h>
#include <linux/if_xdp.h>

int main(void){
    int s = socket(AF_XDP, SOCK_RAW|SOCK_CLOEXEC, 0);
    if (s >= 0){
        struct sockaddr_xdp b;
        memset(&b, 0, sizeof(b));
        b.sxdp_family = AF_XDP;
        b.sxdp_flags = (SXDP_FLAGS);
        b.sxdp_ifindex = 0;
        b.sxdp_queue_id = 0;
        (void)bind(s, (struct sockaddr*)&b, sizeof(b));

        int sz = 1;
        (void)setsockopt(s, SOL_XDP, XDP_RX_RING, &sz, sizeof(sz));
        (void)setsockopt(s, SOL_XDP, XDP_TX_RING, &sz, sizeof(sz));
        (void)setsockopt(s, SOL_XDP, XDP_UMEM_FILL_RING, &sz, sizeof(sz));
        (void)setsockopt(s, SOL_XDP, XDP_UMEM_COMPLETION_RING, &sz, sizeof(sz));

        struct xdp_umem_reg reg;
        memset(&reg, 0, sizeof(reg));
        reg.len = 4096;
        reg.chunk_size = 2048;
        (void)setsockopt(s, SOL_XDP, XDP_UMEM_REG, &reg, sizeof(reg));

        char offbuf[sizeof(struct xdp_mmap_offsets)];
        socklen_t offlen = sizeof(offbuf);
        (void)getsockopt(s, SOL_XDP, XDP_MMAP_OFFSETS, offbuf, &offlen);
        char statbuf[sizeof(struct xdp_statistics)];
        socklen_t statlen = sizeof(statbuf);
        (void)getsockopt(s, SOL_XDP, XDP_STATISTICS, statbuf, &statlen);

        (void)close(s);
    }
    return 0;
}
""").lstrip()

for name, flags in sxdp_combos:
    csrc = BIND_SXDP_TMPL.replace("SXDP_FLAGS", flags or "0")
    with open(os.path.join(OUTDIR, f"bind_sxdp_{name}.c"), "w") as f:
        f.write(csrc)

umem_bits = [
    ("XDP_UMEM_UNALIGNED_CHUNK_FLAG", 1 << 0),
    ("XDP_UMEM_USES_NEED_WAKEUP", 1 << 1),
]

umem_combos = []
for m in range(1 << len(umem_bits)):
    names = [n for i,(n,_) in enumerate(umem_bits) if m & (1 << i)]
    n = "none" if not names else "_".join(x.lower() for x in names)
    v = " | ".join(names) if names else "0"
    umem_combos.append((n, v))

UMEM_TMPL = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <linux/net.h>
#include <linux/socket.h>
#include <linux/if_xdp.h>

int main(void){
    int s = socket(AF_XDP, SOCK_RAW|SOCK_CLOEXEC, 0);
    if (s >= 0){
        struct xdp_umem_reg reg;
        memset(&reg, 0, sizeof(reg));
        reg.len = 4096;
        reg.chunk_size = 2048;
        reg.flags = (UMEM_FLAGS);
        (void)setsockopt(s, SOL_XDP, XDP_UMEM_REG, &reg, sizeof(reg));
        (void)close(s);
    }
    return 0;
}
""").lstrip()

for name, flags in umem_combos:
    csrc = UMEM_TMPL.replace("UMEM_FLAGS", flags)
    with open(os.path.join(OUTDIR, f"umemreg_flags_{name}.c"), "w") as f:
        f.write(csrc)

MMAP_NAMES = [
    ("rx", "XDP_PGOFF_RX_RING"),
    ("tx", "XDP_PGOFF_TX_RING"),
    ("fill", "XDP_UMEM_PGOFF_FILL_RING"),
    ("comp", "XDP_UMEM_PGOFF_COMPLETION_RING"),
]

MMAP_TMPL = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <linux/net.h>
#include <linux/socket.h>
#include <linux/if_xdp.h>

int main(void){
    int s = socket(AF_XDP, SOCK_RAW|SOCK_CLOEXEC, 0);
    if (s >= 0){
        int sz = 1;
        (void)setsockopt(s, SOL_XDP, XDP_RX_RING, &sz, sizeof(sz));
        (void)setsockopt(s, SOL_XDP, XDP_TX_RING, &sz, sizeof(sz));
        (void)setsockopt(s, SOL_XDP, XDP_UMEM_FILL_RING, &sz, sizeof(sz));
        (void)setsockopt(s, SOL_XDP, XDP_UMEM_COMPLETION_RING, &sz, sizeof(sz));

        (void)mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_SHARED, s, (OFFS));
        (void)close(s);
    }
    return 0;
}
""").lstrip()

for nm, offs in MMAP_NAMES:
    csrc = MMAP_TMPL.replace("OFFS", offs)
    with open(os.path.join(OUTDIR, f"mmap_offset_{nm}.c"), "w") as f:
        f.write(csrc)
