import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_phonet"
os.makedirs(OUTDIR, exist_ok=True)

COMMON = dedent(r"""
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>

#include <linux/socket.h>
#include <linux/net.h>
#include <linux/phonet.h>

#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 02000000
#endif
#ifndef SOCK_NONBLOCK
#define SOCK_NONBLOCK 00004000
#endif

static int s_phonet_dgram(void){
    return socket(AF_PHONET, SOCK_DGRAM|SOCK_CLOEXEC|SOCK_NONBLOCK, PN_PROTO_PHONET);
}
static int s_phonet_pipe(void){
    return socket(AF_PHONET, SOCK_SEQPACKET|SOCK_CLOEXEC|SOCK_NONBLOCK, PN_PROTO_PIPE);
}

static void fill_zero_sockaddr_pn(struct sockaddr_pn *sa){
    memset(sa, 0, sizeof(*sa));
    sa->spn_family = AF_PHONET;
    sa->spn_obj = 0;
    sa->spn_dev = 0;
    sa->spn_resource = 0;
}
""").lstrip()

def w(name, body):
    with open(os.path.join(OUTDIR, name), "w") as f:
        f.write(body)

w("phonet_dgram_create.c", COMMON + r"""
int main(void){
    int s = s_phonet_dgram();
    if (s >= 0) close(s);
    return 0;
}
""")

w("phonet_dgram_bind_send_recv.c", COMMON + r"""
int main(void){
    int s = s_phonet_dgram();
    if (s < 0) return 0;

    struct sockaddr_pn sa; fill_zero_sockaddr_pn(&sa);
    (void)bind(s, (struct sockaddr*)&sa, sizeof(sa));

    char buf[1] = {0};
    (void)sendto(s, buf, sizeof(buf), 0, (struct sockaddr*)&sa, sizeof(sa));
    (void)recvfrom(s, buf, sizeof(buf), 0, NULL, 0);

    close(s);
    return 0;
}
""")

w("phonet_dgram_ioctls.c", COMMON + r"""
int main(void){
    int s = s_phonet_dgram();
    if (s < 0) return 0;

    short obj = 0;
    (void)ioctl(s, SIOCPNGETOBJECT, &obj);

    int res_id = 0;
    (void)ioctl(s, SIOCPNDELRESOURCE, &res_id);

    close(s);
    return 0;
}
""")

w("phonet_dgram_ioctl_addresource.c", COMMON + r"""
int main(void){
    int s = s_phonet_dgram();
    if (s < 0) return 0;

    int res_id = 0;
    (void)ioctl(s, SIOCPNGETOBJECT, &res_id);

    close(s);
    return 0;
}
""")

w("phonet_pipe_create.c", COMMON + r"""
int main(void){
    int s = s_phonet_pipe();
    if (s >= 0) close(s);
    return 0;
}
""")

w("phonet_pipe_connect_accept.c", COMMON + r"""
int main(void){
    int s = s_phonet_pipe();
    if (s < 0) return 0;

    struct sockaddr_pn sa; fill_zero_sockaddr_pn(&sa);
    (void)connect(s, (struct sockaddr*)&sa, sizeof(sa));
    (void)ioctl(s, SIOCPNENABLEPIPE, 0);

    (void)accept(s, NULL, NULL);
    (void)accept4(s, NULL, NULL, SOCK_NONBLOCK|SOCK_CLOEXEC);

    close(s);
    return 0;
}
""")

w("phonet_pipe_opt_encap.c", COMMON + r"""
int main(void){
    int s = s_phonet_pipe();
    if (s < 0) return 0;

    int v = 0;
    (void)setsockopt(s, SOL_PNPIPE, PNPIPE_ENCAP, &v, sizeof(v));
    socklen_t l = sizeof(v);
    (void)getsockopt(s, SOL_PNPIPE, PNPIPE_ENCAP, &v, &l);

    close(s);
    return 0;
}
""")

w("phonet_pipe_opt_handle.c", COMMON + r"""
int main(void){
    int s = s_phonet_pipe();
    if (s < 0) return 0;

    int v = 0;
    (void)setsockopt(s, SOL_PNPIPE, PNPIPE_HANDLE, &v, sizeof(v));
    socklen_t l = sizeof(v);
    (void)getsockopt(s, SOL_PNPIPE, PNPIPE_HANDLE, &v, &l);

    close(s);
    return 0;
}
""")

w("phonet_pipe_opt_initstate.c", COMMON + r"""
int main(void){
    int s = s_phonet_pipe();
    if (s < 0) return 0;

    int v = 0;
    (void)setsockopt(s, SOL_PNPIPE, PNPIPE_INITSTATE, &v, sizeof(v));
    socklen_t l = sizeof(v);
    (void)getsockopt(s, SOL_PNPIPE, PNPIPE_INITSTATE, &v, &l);

    close(s);
    return 0;
}
""")

w("phonet_pipe_opt_ifindex_get.c", COMMON + r"""
int main(void){
    int s = s_phonet_pipe();
    if (s < 0) return 0;

    int ifx = 0;
    socklen_t l = sizeof(ifx);
    (void)getsockopt(s, SOL_PNPIPE, PNPIPE_IFINDEX, &ifx, &l);

    close(s);
    return 0;
}
""")
