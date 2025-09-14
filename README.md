# MimicCall: Bypassing System Call Filters via Kernel Function Redundancy

The artifact includes our automated toolchain for identifying MimicCalls (Section 3), experimental evaluation (Section 4), and case studies on real-world CVEs (Section 5).

---

## Repository Structure

* install.sh   # Installation script (one-click setup)
* tool         # Section 3: Automated MimicCall analysis tool
* evaluation   # Section 4: Large-scale evaluation results
* case\_study   # Section 5: Case studies on real-world CVEs

---

## install.sh

Automates the full installation and environment setup:

* Installs required tracing tools.
* Prepares the kernel environment.
* Generates the syscall-to-function database.

Running this script will fully prepare the tool as described in Section 3.

---

## tool/

Implements the MimicCall identification framework (Section 3).
It parses Syzkaller syscall descriptions, generates valid test cases, traces execution with ftrace, and builds a syscall-to-function database.

---

## evaluation/

Contains scripts and data to reproduce our large-scale evaluation (Section 4).
See evaluation/README.md for detailed instructions.

---

## case\_study/

Provides proof-of-concept reproductions of CVE-based case studies (Section 5).
Each subfolder contains exploit variants demonstrating MimicCall bypasses.
See case\_study/README.md for details.

---

## Requirements

* Operating System: Linux (tested on Ubuntu 16.04, 18.04, 20.04 with kernels 4.4.0, 5.4.0, 5.15.0).
* Hardware: Minimum 4 CPU cores and 8 GB RAM (VM-compatible).
* Kernel: Must have CONFIG\_KALLSYMS enabled (default in Ubuntu builds).
* Privileges: Root access required for kernel tracing.
