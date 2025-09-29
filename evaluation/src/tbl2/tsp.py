import os
import csv

VULN_CSV = "./datasets/cve_results.csv"
FILTER_DIR = "./datasets/filters/TSP"

def load_vuln_data():
    vuln_map = {}
    with open(VULN_CSV, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            func = row["해당함수"].strip()
            syscalls = set(s.strip() for s in row["시스템콜 목록"].split(",") if s.strip())
            if len(syscalls) < 2:
                continue
            vuln_map[func] = syscalls
    return vuln_map

def load_tsp_syscalls(path):
    try:
        with open(path, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except Exception as e:
        print(f"[!] {path} 파싱 실패: {e}")
        return set()

def evaluate_tsp():
    vuln_data = load_vuln_data()
    total_filters = 0
    vuln_binaries = 0
    filters_with_mimiccall = 0
    unprotected_funcs = set()

    func_count_by_binary = {}

    for binary in os.listdir(FILTER_DIR):
        binary_dir = os.path.join(FILTER_DIR, binary)
        out_path = os.path.join(binary_dir, "fixed_mainloop.txt")
        if not os.path.isfile(out_path):
            continue

        allowed_syscalls = load_tsp_syscalls(out_path)
        if not allowed_syscalls:
            continue

        total_filters += 1
        has_mimic = False
        allowed_funcs = set()

        for func, syscalls in vuln_data.items():
            if syscalls & allowed_syscalls:
                allowed_funcs.add(func)
                has_mimic = True

        if has_mimic:
            filters_with_mimiccall += 1
            vuln_binaries += 1
            unprotected_funcs.update(allowed_funcs)

        func_count_by_binary[binary] = len(allowed_funcs)

    print("Tool: TSP (fixed_mainloop 기준)")
    print(f"# of Filters (Binaries): {total_filters}")
    print(f"# of Vulnerable Binaries: {vuln_binaries}")
    print(f"# of Filters Including MimicCall: {filters_with_mimiccall}")
    print(f"# of Triggered Vulnerable Functions: {len(unprotected_funcs)}")

    if func_count_by_binary:
        sorted_by_count = sorted(func_count_by_binary.items(), key=lambda x: x[1])
        min_binary, min_count = sorted_by_count[0]
        max_binary, max_count = sorted_by_count[-1]

        print(f"[+] Min vulnerable functions per filter: {min_count} (Binary: {min_binary})")
        print(f"[+] Max vulnerable functions per filter: {max_count} (Binary: {max_binary})")

        avg = sum(func_count_by_binary.values()) / len(func_count_by_binary)
        print(f"[+] Avg vulnerable functions per filter: {avg:.2f}")

if __name__ == "__main__":
    evaluate_tsp()
