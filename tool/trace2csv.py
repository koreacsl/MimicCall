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

function_pattern = re.compile(r"\((\d+)\)\s+([\w\d_.]+)")
syscall_prefix_pattern = re.compile(r"__x64_sys_([\w\d_]+)")


def parse_syscall_trace(filepath):
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return []

    in_syscall_block = False
    current_syscall = None
    base_indent = -1

    for line in lines:
        match = function_pattern.search(line)
        if not match:
            continue
        
        indent_level = line.find(match.group(0))
        _, function = match.groups()
        syscall_match = syscall_prefix_pattern.match(function)
        if syscall_match:
            in_syscall_block = True
            current_syscall = syscall_match.group(1)
            base_indent = indent_level
            continue

        if in_syscall_block and indent_level < base_indent:
            in_syscall_block = False
            current_syscall = None
            base_indent = -1

        if in_syscall_block and indent_level >= base_indent:
            filename = os.path.basename(filepath)
            results.append((filename, current_syscall, function))

    return results


for log_folder in log_folders:
    folder_name = os.path.basename(log_folder)
    csv_output_file = os.path.join(eval_output_folder, f"{folder_name}_trace.csv")

    with open(csv_output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "syscall", "function_name"])

        total_rows_written = 0
        for log_file in os.listdir(log_folder):
            log_path = os.path.join(log_folder, log_file)
            if os.path.isfile(log_path) and log_file.endswith(".txt"):
                try:
                    rows = parse_syscall_trace(log_path)
                    if rows:
                        writer.writerows(rows)
                        total_rows_written += len(rows)
                except Exception as e:
                    print(f"Error processing {log_file}: {e}")