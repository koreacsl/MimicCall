import os
import json
import re
import argparse
import sys

parser = argparse.ArgumentParser(description="Find binaries that include/exclude specific syscalls.")
parser.add_argument("--include", required=True, help="Syscall that must be included (e.g., socket)")
parser.add_argument("--exclude", required=True, help="Syscall that must be excluded (e.g., socketpair)")
args = parser.parse_args()

must_include = args.include
must_exclude = args.exclude

def check_tsp():
    print(f"\n[TSP] Binaries including '{must_include}()' and excluding '{must_exclude}()':")
    base_dir = './datasets/filters/TSP'
    target_file = 'fixed_mainloop.txt'
    matched = 0
    total = 0

    for binary in os.listdir(base_dir):
        file_path = os.path.join(base_dir, binary, target_file)
        if not os.path.isfile(file_path):
            continue
        total += 1
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            if must_include in content and must_exclude not in content:
                print(f" - {binary}")
                matched += 1
        except Exception as e:
            print(f"[ERROR:TSP] {binary}: {e}")
    return total, matched

def check_syspart():
    print(f"\n[syspart] Binaries including '{must_include}()' and excluding '{must_exclude}()':")
    base_dir = './datasets/filters/syspart'
    target_file = 'serving_syscalls.out'
    matched = 0
    total = 0

    for binary in os.listdir(base_dir):
        file_path = os.path.join(base_dir, binary, target_file)
        if not os.path.isfile(file_path):
            continue
        total += 1
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            match = re.search(r'SYSCALLS\s*\[([^\]]+)\]', content)
            if match:
                syscalls = [s.strip() for s in match.group(1).split(',') if s.strip()]
                if must_include in syscalls and must_exclude not in syscalls:
                    print(f" - {binary}")
                    matched += 1
        except Exception as e:
            print(f"[ERROR:syspart] {binary}: {e}")
    return total, matched

def check_sysfilter():
    print(f"\n[sysfilter] Binaries including '{must_include}()' and excluding '{must_exclude}()':")
    base_dir = './datasets/filters/sysfilter'
    target_file = 'allowed_syscalls.out'
    matched = 0
    total = 0

    for binary in os.listdir(base_dir):
        binary_path = os.path.join(base_dir, binary)
        syscall_file = os.path.join(binary_path, target_file)
        if not os.path.isdir(binary_path) or not os.path.isfile(syscall_file):
            continue
        total += 1
        try:
            with open(syscall_file, 'r') as f:
                syscalls = set(line.strip() for line in f.readlines())
            if must_include in syscalls and must_exclude not in syscalls:
                print(f" - {binary}")
                matched += 1
        except Exception as e:
            print(f"[ERROR:sysfilter] {binary}: {e}")
    return total, matched

def check_confine():
    print(f"\n[Confine] JSON files blacklisting '{must_exclude}()' and not blacklisting '{must_include}()':")
    base_dir = './datasets/filters/confine'
    matched = 0
    total = 0

    for filename in os.listdir(base_dir):
        if not filename.endswith('.json'):
            continue
        filepath = os.path.join(base_dir, filename)
        total += 1
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            syscalls = {entry['name'] for entry in data.get('syscalls', []) if 'name' in entry}
            if must_exclude in syscalls and must_include not in syscalls:
                print(f" - {filename}")
                matched += 1
        except Exception as e:
            print(f"[ERROR:confine] {filename}: {e}")
    return total, matched

def check_c2c():
    print(f"\n[C2C] Binaries including '{must_include}()' and excluding '{must_exclude}()':")
    base_dir = './datasets/filters/C2C'
    target_phase = 'piecewiseMaster'
    matched = 0
    total = 0

    for root, _, files in os.walk(base_dir):
        for file in files:
            if not file.endswith('.syscall.out'):
                continue
            filepath = os.path.join(root, file)
            binary_name = os.path.basename(root)
            total += 1
            try:
                with open(filepath, 'r') as f:
                    data = eval(f.read())
                if not isinstance(data, dict) or target_phase not in data:
                    continue
                syscalls = set(data[target_phase])
                if must_include in syscalls and must_exclude not in syscalls:
                    print(f" - {binary_name}")
                    matched += 1
            except Exception as e:
                print(f"[ERROR:C2C] {binary_name}: {e}")
    return total, matched

if __name__ == '__main__':
    summary = {}
    summary['TSP'] = check_tsp()
    summary['syspart'] = check_syspart()
    summary['sysfilter'] = check_sysfilter()
    summary['Confine'] = check_confine()
    summary['C2C'] = check_c2c()

    output_dir = './claim'
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"tbl3_{must_include}_{must_exclude}.txt"
    output_filepath = os.path.join(output_dir, output_filename)

    summary_lines = ["Summary:"]
    for tool, (total, matched) in summary.items():
        if total > 0:
            percentage = (matched / total) * 100
            summary_lines.append(f" - {tool}: {matched} / {total} matched ({percentage:.1f}%)")
        else:
            summary_lines.append(f" - {tool}: no data")

    summary_text = "\n".join(summary_lines)
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        print("\n" + summary_text)
        print(f"\nSummary saved to {output_filepath}")
    except Exception as e:
        print(f"\n[ERROR] Failed to write summary to file: {e}")
