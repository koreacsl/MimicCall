# 🎭 MimicCall: Bypassing System Call Filters via Kernel Function Redundancy

> **Note**
> This research will be presented at the **41th Annual Computer Security Applications Conference (ACSAC 2025)**.

## 📜 About the Paper

Modern operating systems widely employ system call filtering to reduce the kernel attack surface. However, existing filters operate at the system call 'interface' level and overlook the fact that multiple system calls often 'share' internal kernel functions.

This paper introduces **MimicCall**, a novel filter bypass technique. A MimicCall is an **allowed system call that, unbeknownst to the filter, invokes the same vulnerable internal function as a blocked system call**, thus bypassing the filter. This research reveals a fundamental limitation in system-call-level defenses.

## 🛠️ About this Tool

This repository contains the official artifact (tool) for the MimicCall paper.

The purpose of this tool is to provide an analysis framework that automatically identifies MimicCalls. Its goal is to **build a database that maps system calls to the internal kernel functions they invoke** within a specific kernel environment.

It operates as follows:

1.  **Test Case Generation:** It parses Syzkaller's system call descriptions to automatically generate C test code with diverse argument configurations.
2.  **Dynamic Tracing:** It executes the generated test cases while using `ftrace` to trace the call paths of all internal kernel functions invoked by that system call.
3.  **Database Construction:** The collected trace information is normalized to create a 'Syscall-Function DB'.

An analyst (or attacker) can then query this database to identify all system calls (i.e., potential MimicCalls) that can reach a specific vulnerable function (Root Cause Function).

## 🚀 Getting Started

This `main` branch contains the MimicCall analysis tool.

To set up the necessary environment and install dependencies for running the tool, please first execute the `install.sh` script located in the root directory.

```bash
./install.sh
```
