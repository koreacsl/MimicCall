import os
from textwrap import dedent
from itertools import product

OUTDIR = "./tool/cfiles/socket_vnet"
os.makedirs(OUTDIR, exist_ok=True)

ACCEPT_FLAG_SETS = [
    ("none", 0),
    ("cloexec", "SOCK_CLOEXEC"),
    ("nonblock", "SOCK_NONBLOCK"),
    ("cloexec_nonblock", "(SOCK_CLOEXEC|SOCK_NONBLOCK)"),
]

ACCEPT4_C = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <linux/net.h>
#include <linux/socket.h>
#include <linux/vm_sockets.h>

static int do_one(void){
    int s = socket(AF_VSOCK, SOCK_STREAM|SOCK_CLOEXEC, 0);
    if (s >= 0) {
        struct sockaddr_vm a;
        memset(&a, 0, sizeof(a));
        a.svm_family = AF_VSOCK;
        a.svm_cid = VMADDR_CID_ANY;
        a.svm_port = VMADDR_PORT_ANY;
        (void)bind(s, (struct sockaddr*)&a, sizeof(a));
        (void)listen(s, 1);
        (void)accept4(s, NULL, NULL, ACCFLAGS);
        close(s);
    }
    return 0;
}
int main(void){ return do_one(); }
""").lstrip()

for name, flags in ACCEPT_FLAG_SETS:
    csrc = ACCEPT4_C.replace("ACCFLAGS", str(flags))
    path = os.path.join(OUTDIR, f"vsock_accept4_{name}.c")
    with open(path, "w") as f:
        f.write(csrc)

VHOST_BITS = [
    ("VHOST_LOG_ALL",          "VHOST_LOG_ALL"),
    ("VIRTIO_NOTIFY_ON_EMPTY", "VIRTIO_NOTIFY_ON_EMPTY"),
    ("VIRTIO_RING_F_INDIRECT_DESC", "VIRTIO_RING_F_INDIRECT_DESC"),
    ("VIRTIO_RING_F_EVENT_IDX", "VIRTIO_RING_F_EVENT_IDX"),
    ("VIRTIO_ANY_LAYOUT",      "VIRTIO_ANY_LAYOUT"),
    ("VIRTIO_VERSION_1",       "VIRTIO_VERSION_1"),
    ("VHOST_NET_VIRTIO_NET_HDR","VHOST_NET_VIRTIO_NET_HDR"),
    ("VIRTIO_NET_MRG_RXBUF",   "VIRTIO_NET_MRG_RXBUF"),
    ("VIRTIO_IOMMU_PLATFORM",  "VIRTIO_IOMMU_PLATFORM"),
]

FEATURES_C = dedent(r"""
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/virtio_config.h>
#include <linux/vhost.h>

#ifndef O_CLOEXEC
#define O_CLOEXEC 02000000
#endif

static int do_one(void){
    int fd = open("/dev/vhost-vsock", O_RDWR|O_CLOEXEC);
    if (fd < 0) fd = open("/dev/vhost-net", O_RDWR|O_CLOEXEC);
    if (fd >= 0){
        (void)ioctl(fd, VHOST_SET_OWNER, 0);
        uint64_t features = FEATMASK;
        (void)ioctl(fd, VHOST_SET_FEATURES, &features);
        (void)ioctl(fd, VHOST_RESET_OWNER, 0);
        close(fd);
    }
    return 0;
}
int main(void){ return do_one(); }
""").lstrip()

def mask_to_expr(bits_on):
    if not bits_on:
        return "0"
    return "(" + "|".join(bits_on) + ")"

N = len(VHOST_BITS)
for m in range(1<<N):
    on = []
    tag = []
    for i, (_, macro) in enumerate(VHOST_BITS):
        if (m >> i) & 1:
            on.append(macro)
            tag.append(str(i))
    fname_tag = "none" if not tag else "b" + "_".join(tag)
    mask_expr = mask_to_expr(on)
    csrc = FEATURES_C.replace("FEATMASK", mask_expr)
    path = os.path.join(OUTDIR, f"vhost_features_{fname_tag}.c")
    with open(path, "w") as f:
        f.write(csrc)

IOTLB_PERM = [
    ("ro", "VHOST_ACCESS_RO"),
    ("wo", "VHOST_ACCESS_WO"),
    ("rw", "VHOST_ACCESS_RW"),
]
IOTLB_TYPE = [
    ("miss", "VHOST_IOTLB_MISS"),
    ("update", "VHOST_IOTLB_UPDATE"),
    ("invalidate", "VHOST_IOTLB_INVALIDATE"),
    ("access_fail", "VHOST_IOTLB_ACCESS_FAIL"),
]

IOTLB_C = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/virtio_config.h>
#include <linux/vhost.h>

#ifndef O_CLOEXEC
#define O_CLOEXEC 02000000
#endif

int main(void){
    int fd = open("/dev/vhost-net", O_RDWR|O_CLOEXEC);
    if (fd >= 0){
        struct vhost_msg_v2 msg;
        memset(&msg, 0, sizeof(msg));
        msg.type = VHOST_IOTLB_MSG_V2;
        msg.iotlb.perm = PERM;
        msg.iotlb.type = TYP;
        (void)write(fd, &msg, sizeof(msg));
        close(fd);
    }
    return 0;
}
""").lstrip()

for (pname, pm), (tname, tm) in product(IOTLB_PERM, IOTLB_TYPE):
    csrc = IOTLB_C.replace("PERM", pm).replace("TYP", tm)
    path = os.path.join(OUTDIR, f"vhost_iotlb_{pname}_{tname}.c")
    with open(path, "w") as f:
        f.write(csrc)