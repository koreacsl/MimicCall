import os
import json
import csv

CONFINE_DIR = "./datasets/filters/confine"
VULN_CSV_PATH = "./datasets/cve_results.csv"

# === 1. CSV 파일에서 취약 함수와 해당 시스템콜 목록 읽기 ===
func_to_syscalls = {}
with open(VULN_CSV_PATH, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        func = row['해당함수'].strip()
        syscalls = [s.strip() for s in row['시스템콜 목록'].split(',')]
        if len(set(syscalls)) >= 2:  # MimicCall 가능한 경우만 사용
            func_to_syscalls[func] = set(syscalls)

all_mimic_syscalls = set()
for s in func_to_syscalls.values():
    all_mimic_syscalls.update(s)

# === 2. 필터 파일들 분석 ===
vulnerable_binary_count = 0
filters_with_mimiccall = 0
triggered_vuln_functions = set()
total_binaries = 0
func_count_by_binary = {}  # ✅ 바이너리별 허용된 취약 함수 수

for fname in os.listdir(CONFINE_DIR):
    if not fname.endswith(".json"):
        continue
    total_binaries += 1

    path = os.path.join(CONFINE_DIR, fname)
    try:
        with open(path) as f:
            data = json.load(f)
            blocked = {s["name"] for s in data.get("syscalls", []) if s["action"] == "SCMP_ACT_ERRNO"}
    except Exception as e:
        print(f"[!] {fname} 파싱 실패: {e}")
        continue

    allowed = all_mimic_syscalls - blocked

    this_binary_triggered_funcs = set()
    for func, syscalls in func_to_syscalls.items():
        if syscalls & allowed:
            this_binary_triggered_funcs.add(func)

    if this_binary_triggered_funcs:
        vulnerable_binary_count += 1
        filters_with_mimiccall += 1
        triggered_vuln_functions.update(this_binary_triggered_funcs)

    binary_name = os.path.splitext(fname)[0]  # 예: nginx.json → nginx
    func_count_by_binary[binary_name] = len(this_binary_triggered_funcs)

# === 3. 출력 ===
print(f"Tool: Confine")
print("Total CVE functions with ≥2 syscalls:", len(func_to_syscalls))
print(f"# of Filters (Binaries): {total_binaries}")
print(f"# of Vulnerable Binaries: {vulnerable_binary_count}")
print(f"# of Filters Including MimicCall: {filters_with_mimiccall}")
print(f"# of Triggered Vulnerable Functions: {len(triggered_vuln_functions)}")

if func_count_by_binary:
    sorted_by_count = sorted(func_count_by_binary.items(), key=lambda x: x[1])
    min_binary, min_count = sorted_by_count[0]
    max_binary, max_count = sorted_by_count[-1]
    avg = sum(func_count_by_binary.values()) / len(func_count_by_binary)

    print(f"[+] Min vulnerable functions per filter: {min_count} (Binary: {min_binary})")
    print(f"[+] Max vulnerable functions per filter: {max_count} (Binary: {max_binary})")
    print(f"[+] Avg vulnerable functions per filter: {avg:.2f}")
