import os
from textwrap import dedent

OUTDIR = "./tool/cfiles/socket_rxrpc"
os.makedirs(OUTDIR, exist_ok=True)

PROTOS = ["AF_INET", "AF_INET6"]
TOGGLE_OPTS = ["exclusive", "key", "keyring", "upgradeable"]
MINSEC_LEVELS = ["none", "plain", "encrypt"]

C_TEMPLATE = dedent(r"""
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#include <linux/socket.h>
#include <linux/net.h>
#include <linux/rxrpc.h>

#ifndef AF_RXRPC
#define AF_RXRPC 40
#endif
#ifndef SOL_RXRPC
#define SOL_RXRPC 278
#endif

typedef uint16_t rxrpc_service;

static void fill_rxrpc_in4(struct sockaddr_rxrpc* srx) {{
    memset(srx, 0, sizeof(*srx));
    srx->srx_family = AF_RXRPC;
    srx->srx_service = 0;
    srx->transport_type = SOCK_DGRAM;
    struct sockaddr_in *in = (struct sockaddr_in *)&srx->transport;
    memset(in, 0, sizeof(*in));
    in->sin_family = AF_INET;
    in->sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    in->sin_port = htons(0);
    srx->transport_len = sizeof(*in);
}}

static void fill_rxrpc_in6(struct sockaddr_rxrpc* srx) {{
    memset(srx, 0, sizeof(*srx));
    srx->srx_family = AF_RXRPC;
    srx->srx_service = 0;
    srx->transport_type = SOCK_DGRAM;
    struct sockaddr_in6 *in6 = (struct sockaddr_in6 *)&srx->transport;
    memset(in6, 0, sizeof(*in6));
    in6->sin6_family = AF_INET6;
    in6->sin6_addr = in6addr_loopback;
    in6->sin6_port = htons(0);
    srx->transport_len = sizeof(*in6);
}}

int main(void){{
    int s = socket(AF_RXRPC, SOCK_DGRAM, {proto_flag});
    if (s < 0) return 0;

    struct sockaddr_rxrpc srx;
#if {use_inet4}
    fill_rxrpc_in4(&srx);
#else
    fill_rxrpc_in6(&srx);
#endif

    (void)bind(s, (struct sockaddr*)&srx, sizeof(srx));
    (void)connect(s, (struct sockaddr*)&srx, sizeof(srx));

#if {do_exclusive}
    (void)setsockopt(s, SOL_RXRPC, RXRPC_EXCLUSIVE_CONNECTION, NULL, 0);
#endif

#if {do_key}
    static const char keystr[] = "k";
    (void)setsockopt(s, SOL_RXRPC, RXRPC_SECURITY_KEY, keystr, sizeof(keystr));
#endif

#if {do_keyring}
    static const char kr[] = "_kr";
    (void)setsockopt(s, SOL_RXRPC, RXRPC_SECURITY_KEYRING, kr, sizeof(kr));
#endif

#if {do_minsec}
    {{
        int lvl = {minsec_value};
        (void)setsockopt(s, SOL_RXRPC, RXRPC_MIN_SECURITY_LEVEL, &lvl, sizeof(lvl));
    }}
#endif

#if {do_upgrade}
    {{
        rxrpc_service sv[2] = {{0, 0}};
        (void)setsockopt(s, SOL_RXRPC, RXRPC_UPGRADEABLE_SERVICE, sv, sizeof(sv));
    }}
#endif

    close(s);
    return 0;
}}
""").lstrip()

def make_filename(proto, exclusive, key, keyring, minsec, upgradeable):
    parts = [proto.lower().replace('af_', '')]
    if exclusive: parts.append("exclusive")
    if key: parts.append("key")
    if keyring: parts.append("keyring")
    parts.append(f"minsec_{minsec}")
    if upgradeable: parts.append("upgrade")
    return "rxrpc_" + "_".join(parts) + ".c"

count = 0
for proto in PROTOS:
    for exclusive in (0, 1):
        for key in (0, 1):
            for keyring in (0, 1):
                for minsec in MINSEC_LEVELS:
                    for upgradeable in (0, 1):
                        
                        minsec_setting = {
                            "none": ("0", "RXRPC_SECURITY_PLAIN"),
                            "plain": ("1", "RXRPC_SECURITY_PLAIN"),
                            "encrypt": ("1", "RXRPC_SECURITY_ENCRYPT")
                        }[minsec]

                        src = C_TEMPLATE.format(
                            proto_flag=proto,
                            use_inet4=1 if proto == "AF_INET" else 0,
                            do_exclusive=exclusive,
                            do_key=key,
                            do_keyring=keyring,
                            do_upgrade=upgradeable,
                            do_minsec=minsec_setting[0],
                            minsec_value=minsec_setting[1]
                        )

                        fname = make_filename(proto, exclusive, key, keyring, minsec, upgradeable)
                        with open(os.path.join(OUTDIR, fname), "w") as f:
                            f.write(src)
                        count += 1