# Case Study — README

**Warning:** Run these PoCs only in an isolated test environment (VM/QEMU or disposable machine). They may crash the kernel or escalate privileges.

---

## CVE-2016-4486

**Compile & run**

```bash
# compile
gcc exploit.c -o exploit

# run
./exploit
```

**Expected result**

* PoC prints leaked kernel stack data / uninitialized stack bytes (information disclosure). May show addresses or raw bytes useful for ASLR analysis. No special capabilities required.

---

## CVE-2016-9793

**Compile & run**

```bash
# compile
gcc -pthread exploit.c -o exploit

# grant capability and run
sudo setcap cap_net_admin+ep ./exploit
./exploit
```

**Expected result**

* Exploit triggers mishandling of negative buffer-size in `setsockopt()`; outcomes can include kernel panic (DoS), memory corruption, or privileged-impact behavior depending on kernel/version. Requires `CAP_NET_ADMIN` (provided via `setcap`).

---

## CVE-2017-7184

**Compile & run**

```bash
# compile
gcc -o exploit exploit.c

# grant capabilities
sudo setcap cap_net_raw,cap_net_admin+ep ./exploit

# (if needed) verify/load modules
lsmod | egrep '(^ah4|xfrm_)'
sudo modprobe ah4 xfrm_user xfrm4_mode_transport

# run
./exploit
```

**Expected result**

* PoC sends malformed XFRM messages causing heap out-of-bounds access. Common outcomes: kernel panic (DoS) or memory corruption; exploit reliability depends on kernel configuration and loaded modules. `CAP_NET_ADMIN`/`cap_net_raw` typically required.
