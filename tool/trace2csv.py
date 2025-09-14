import os
import csv
import re

base_log_folder = "./tool/trace"
eval_output_folder = "./tool/csvs"
os.makedirs(eval_output_folder, exist_ok=True)

log_folders = [
    os.path.join(base_log_folder, folder)
    for folder in os.listdir(base_log_folder)
    if os.path.isdir(os.path.join(base_log_folder, folder))
]

function_pattern = re.compile(r"\s*[\+\-]*\((\d+)\)\s+([\w\d_.]+)")
syscall_prefix_pattern = re.compile(r"__x64_sys_([\w\d_]+)")

def parse_syscall_trace(filepath):
    results = []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_syscall_block = False
    current_syscall = None
    base_indent = None

    for line in lines:
        match = function_pattern.search(line)
        if not match:
            continue

        indent_level = line.index(match.group(0))
        _, function = match.groups()

        if function == "x64_sys_call":
            in_syscall_block = True
            current_syscall = None
            base_indent = indent_level
            continue

        if in_syscall_block and current_syscall is None:
            match_syscall = syscall_prefix_pattern.match(function)
            if match_syscall:
                current_syscall = match_syscall.group(1)
                continue

        if in_syscall_block and current_syscall:
            if indent_level <= base_indent:
                in_syscall_block = False
                current_syscall = None
                continue
            results.append((os.path.basename(filepath), current_syscall, function))

    return results

for log_folder in log_folders:
    folder_name = os.path.basename(log_folder)
    csv_output_file = os.path.join(eval_output_folder, f"{folder_name}_trace.csv")

    with open(csv_output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "syscall", "function_name"])

        for log_file in os.listdir(log_folder):
            log_path = os.path.join(log_folder, log_file)
            if os.path.isfile(log_path) and log_file.endswith(".txt"):
                print(f"Processing {log_file}...")
                try:
                    rows = parse_syscall_trace(log_path)
                    writer.writerows(rows)
                except Exception as e:
                    print(f"Error in {log_file}: {e}")