import os
import csv

VULN_CSV = "./datasets/cve_results.csv"
FILTER_DIR = "./datasets/filters/C2C"

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

def load_piecewise_master(out_path):
    with open(out_path, "r") as f:
        try:
            raw = eval(f.read())
            return set(raw.get("piecewiseMaster", []))
        except Exception as e:
            print(f"[!] {out_path} 파싱 실패: {e}")
            return set()

def evaluate_piecewise_master():
    vuln_data = load_vuln_data()
    total_filters = 0
    vuln_binaries = 0
    filters_with_mimiccall = 0
    unprotected_funcs = set()
    func_count_by_filter = {}

    for root, _, files in os.walk(FILTER_DIR):
        for file in files:
            if not file.endswith(".out"):
                continue

            path = os.path.join(root, file)
            allowed = load_piecewise_master(path)
            if not allowed:
                continue

            total_filters += 1
            has_mimic = False
            allowed_funcs = set()

            for func, syscalls in vuln_data.items():
                if syscalls & allowed:
                    allowed_funcs.add(func)
                    has_mimic = True

            if has_mimic:
                filters_with_mimiccall += 1
                vuln_binaries += 1
                unprotected_funcs.update(allowed_funcs)

            filter_name = os.path.relpath(path, FILTER_DIR)
            func_count_by_filter[filter_name] = len(allowed_funcs)

    print("Tool: C2C (piecewiseMaster 기준)")
    print(f"# of Filters (Binaries): {total_filters}")
    print(f"# of Vulnerable Binaries: {vuln_binaries}")
    print(f"# of Filters Including MimicCall: {filters_with_mimiccall}")
    print(f"# of Triggered Vulnerable Functions: {len(unprotected_funcs)}")

    if func_count_by_filter:
        sorted_by_count = sorted(func_count_by_filter.items(), key=lambda x: x[1])
        min_filter, min_count = sorted_by_count[0]
        max_filter, max_count = sorted_by_count[-1]
        avg = sum(func_count_by_filter.values()) / len(func_count_by_filter)

        print(f"[+] Min vulnerable functions per filter: {min_count} (Filter: {min_filter})")
        print(f"[+] Max vulnerable functions per filter: {max_count} (Filter: {max_filter})")
        print(f"[+] Avg vulnerable functions per filter: {avg:.2f}")

if __name__ == "__main__":
    evaluate_piecewise_master()