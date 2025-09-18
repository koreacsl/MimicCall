import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_unix"
os.makedirs(OUTDIR, exist_ok=True)

SOCK_TYPES = [
    ("stream",   "SOCK_STREAM"),
    ("dgram",    "SOCK_DGRAM"),
    ("seqpacket","SOCK_SEQPACKET"),
]

FAMILIES = [
    ("af_unix",   "AF_UNIX"),
    ("af_unspec", "AF_UNSPEC"),
]

C_TMPL = dedent(r"""
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <sys/un.h>
#include <linux/net.h>

static int run_test(void) {
    int s = socket(AF_UNIX, SOCKTYPE | SOCK_CLOEXEC, 0);
    if (s >= 0) {
        struct sockaddr_un su;
        memset(&su, 0, sizeof(su));
        su.sun_family = FAMILY;
        su.sun_path[0] = '\0';
        su.sun_path[1] = 'x';
        (void)bind(s, (struct sockaddr *)&su, sizeof(sa_family_t) + 2);
        (void)connect(s, (struct sockaddr *)&su, sizeof(sa_family_t) + 2);

        struct sockaddr_un out;
        socklen_t olen = sizeof(out);
        (void)getsockname(s, (struct sockaddr *)&out, &olen);
        olen = sizeof(out);
        (void)getpeername(s, (struct sockaddr *)&out, &olen);

        struct iovec iov = { .iov_base = (void*)"", .iov_len = 0 };
        struct msghdr sm = {0};
        sm.msg_iov = &iov;
        sm.msg_iovlen = 1;
        (void)sendmsg(s, &sm, MSG_DONTWAIT);

        struct msghdr rm = {0};
        rm.msg_iov = &iov;
        rm.msg_iovlen = 1;
        (void)recvmsg(s, &rm, MSG_DONTWAIT);

        close(s);
    }

    int sp[2];
    if (socketpair(AF_UNIX, SOCKTYPE | SOCK_CLOEXEC, 0, sp) == 0) {
        struct iovec iov = { .iov_base = (void*)"", .iov_len = 0 };
        struct msghdr sm = {0};
        sm.msg_iov = &iov;
        sm.msg_iovlen = 1;
        (void)sendmsg(sp[0], &sm, MSG_DONTWAIT);

        struct msghdr rm = {0};
        rm.msg_iov = &iov;
        rm.msg_iovlen = 1;
        (void)recvmsg(sp[1], &rm, MSG_DONTWAIT);

        struct sockaddr_un out;
        socklen_t olen = sizeof(out);
        (void)getsockname(sp[0], (struct sockaddr *)&out, &olen);
        olen = sizeof(out);
        (void)getpeername(sp[1], (struct sockaddr *)&out, &olen);

        close(sp[0]);
        close(sp[1]);
    }
    return 0;
}

int main(void) { return run_test(); }
""").lstrip()

def emit(fname, sock_macro, family_macro):
    src = (C_TMPL
           .replace("SOCKTYPE", sock_macro)
           .replace("FAMILY", family_macro))
    with open(os.path.join(OUTDIR, fname), "w") as f:
        f.write(src)

count = 0
for st_name, st_macro in SOCK_TYPES:
    for fam_name, fam_macro in FAMILIES:
        filename = f"unix_{st_name}_{fam_name}.c"
        emit(filename, st_macro, fam_macro)
        count += 1