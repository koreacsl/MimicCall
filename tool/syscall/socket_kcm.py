import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_kcm"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/uio.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>

#include <linux/net.h>
#include <linux/kcm.h>
#include <linux/sockios.h>

#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 02000000
#endif

static int s_kcm(int typ){
    int s = socket(AF_KCM, typ | SOCK_CLOEXEC, KCMPROTO_CONNECTED);
    if (s >= 0) {
        int fl = fcntl(s, F_GETFL, 0);
        if (fl >= 0) fcntl(s, F_SETFL, fl | O_NONBLOCK);
    }
    return s;
}
""").lstrip()

def wr(name: str, src: str):
    with open(os.path.join(OUTDIR, name), "w") as f:
        f.write(src)

wr("kcm_socket_dgram.c", COMMON + r"""
int main(void){
    int s = s_kcm(SOCK_DGRAM);
    if (s >= 0) close(s);
    return 0;
}
""")

wr("kcm_socket_seqpacket.c", COMMON + r"""
int main(void){
    int s = s_kcm(SOCK_SEQPACKET);
    if (s >= 0) close(s);
    return 0;
}
""")

wr("setsockopt_kcm_recv_disable.c", COMMON + r"""
int main(void){
    int s = s_kcm(SOCK_DGRAM); if (s < 0) return 0;
    int v = 1;
    (void)setsockopt(s, SOL_KCM, KCM_RECV_DISABLE, &v, sizeof(v));
    close(s);
    return 0;
}
""")

wr("getsockopt_kcm_recv_disable.c", COMMON + r"""
int main(void){
    int s = s_kcm(SOCK_DGRAM); if (s < 0) return 0;
    int v = 0;
    socklen_t len = sizeof(v);
    (void)getsockopt(s, SOL_KCM, KCM_RECV_DISABLE, &v, &len);
    close(s);
    return 0;
}
""")

wr("sendmsg_kcm.c", COMMON + r"""
int main(void){
    int s = s_kcm(SOCK_DGRAM); if (s < 0) return 0;
    char dummy = 0;
    struct iovec iov = {.iov_base = &dummy, .iov_len = 0};
    struct msghdr mh;
    memset(&mh, 0, sizeof(mh));
    mh.msg_iov = &iov;
    mh.msg_iovlen = 1;
    (void)sendmsg(s, &mh, 0);
    close(s);
    return 0;
}
""")

wr("recvmsg_kcm.c", COMMON + r"""
int main(void){
    int s = s_kcm(SOCK_DGRAM); if (s < 0) return 0;
    char buf[16];
    struct iovec iov = {.iov_base = buf, .iov_len = sizeof(buf)};
    struct msghdr mh;
    memset(&mh, 0, sizeof(mh));
    mh.msg_iov = &iov;
    mh.msg_iovlen = 1;
    (void)recvmsg(s, &mh, 0);
    close(s);
    return 0;
}
""")

wr("ioctl_siockcmattach.c", COMMON + r"""
int main(void){
    int s = s_kcm(SOCK_DGRAM); if (s < 0) return 0;
    struct kcm_attach att;
    memset(&att, 0, sizeof(att));
    att.fd = -1;       
    att.bpf_fd = -1; 
    (void)ioctl(s, SIOCKCMATTACH, &att);
    close(s);
    return 0;
}
""")

wr("ioctl_siockcmunattach.c", COMMON + r"""
int main(void){
    int s = s_kcm(SOCK_DGRAM); if (s < 0) return 0;
    struct kcm_unattach ua;
    memset(&ua, 0, sizeof(ua));
    ua.fd = -1;
    (void)ioctl(s, SIOCKCMUNATTACH, &ua);
    close(s);
    return 0;
}
""")

wr("ioctl_siockcmclone.c", COMMON + r"""
int main(void){
    int s = s_kcm(SOCK_DGRAM); if (s < 0) return 0;
    struct kcm_clone cl;
    memset(&cl, 0, sizeof(cl));
    cl.fd = s;  // 커널이 실패해도 호출 경로만 통과하면 됨
    (void)ioctl(s, SIOCKCMCLONE, &cl);
    close(s);
    return 0;
}
""")