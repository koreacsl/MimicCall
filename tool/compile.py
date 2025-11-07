import os
import sys
import subprocess
import shutil
import time
import re
from datetime import datetime

SRC_DIR = "./tool/cfiles"
OUT_DIR = "./tool/exe"
ROOT_OUT_DIR = "./tool/exe_root"
ERROR_LOG = "./tool/compile_error.log"
LONG_LOG = "./tool/long_run.log"
CONSTANTS_FILE = "./tool/combined_constants.txt"

total_compiled = 0
run_success = 0
run_failed = 0
sudo_ran = []

def load_constants(filepath):
    constants = {}
    if not os.path.exists(filepath):
        print(f"Warning: Constants file ({filepath}) not found.")
        return constants

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                match = re.match(r'^([a-zA-Z0-9_]+)\s*=\s*([^,]+)', line)
                if match:
                    const_name = match.group(1)
                    const_value = match.group(2).strip()
                    constants[const_name] = const_value
    except Exception as e:
        print(f"Error loading constants file: {e}")
    print(f"Loaded {len(constants)} constants.")
    return constants

def log_error(message):
    with open(ERROR_LOG, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")

def log_long_run(exe_path, duration):
    with open(LONG_LOG, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now()} - {exe_path} execution time exceeded {duration:.2f}s\n")

def try_run(output_file, rel_path):
    global run_success, run_failed, sudo_ran
    start = time.time()
    try:
        result = subprocess.run([output_file], capture_output=True, text=True, timeout=5)
        duration = time.time() - start
        if duration > 3:
            log_long_run(output_file, duration)
        if result.returncode == 0:
            run_success += 1
        else:
            stderr = result.stderr.strip()
            should_retry_with_sudo = (
                "Operation not permitted" in stderr or
                "Permission denied" in stderr or
                result.returncode != 0
            )
            if should_retry_with_sudo:
                sudo_start = time.time()
                sudo_result = subprocess.run(["sudo", output_file], capture_output=True, text=True, timeout=5)
                sudo_duration = time.time() - sudo_start
                if sudo_duration > 3:
                    log_long_run(output_file + " [sudo]", sudo_duration)
                if sudo_result.returncode == 0:
                    run_success += 1
                    sudo_ran.append(os.path.join(rel_path, os.path.basename(output_file)))
                    dest_dir = os.path.join(ROOT_OUT_DIR, rel_path)
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.move(output_file, os.path.join(dest_dir, os.path.basename(output_file)))
                else:
                    run_failed += 1
            else:
                run_failed += 1
    except subprocess.TimeoutExpired:
        duration = time.time() - start
        log_long_run(output_file, duration)
        run_failed += 1
    except Exception:
        run_failed += 1

def pick_link_libs(folder_name: str):
    name = folder_name.lower()
    libs = set()

    if re.search(r'(^|[_-])(add_key|request_key|keyctl)(_|$)', name):
        libs.add("-lkeyutils")

    if any(tok in name for tok in ["clock", "timer", "mq_", "mq-", "eventfd"]):
        libs.add("-lrt")

    if any(tok in name for tok in ["mbind", "mempolicy", "move_pages", "lnuma", "numa"]):
        libs.add("-lnuma")

    return sorted(libs)

def compile_c_files():
    global total_compiled
    constants_db = load_constants(CONSTANTS_FILE)

    for log in [ERROR_LOG, LONG_LOG]:
        if os.path.exists(log):
            os.remove(log)

    if os.path.exists(ROOT_OUT_DIR):
        pass

    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if not file.endswith(".c"):
                continue

            cfile = os.path.join(root, file)
            rel_path = os.path.relpath(root, SRC_DIR)
            out_dir = os.path.join(OUT_DIR, rel_path)
            os.makedirs(out_dir, exist_ok=True)

            bin_name = os.path.splitext(file)[0]
            output_file = os.path.join(out_dir, bin_name)

            folder_name = os.path.basename(root)
            link_libs = pick_link_libs(folder_name)

            cmd = ["gcc", "-Wall", "-Wextra", "-O2", "-D_GNU_SOURCE", "-pg", "-o", output_file, cfile] + link_libs

            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')

            if result.returncode == 0:
                opts_str = f" ({', '.join(link_libs)})" if link_libs else ""
                print(f"Compile success: {cfile} -> {output_file}{opts_str}")
                total_compiled += 1
                try_run(output_file, rel_path)
            else:
                undeclared_vars = set(re.findall(r"['‘]([^'’]+)['’] undeclared", result.stderr))
                defines_to_add = []
                if undeclared_vars and constants_db:
                    for var in undeclared_vars:
                        if var in constants_db:
                            defines_to_add.append(f"#define {var} {constants_db[var]}\n")

                if defines_to_add:
                    print(f"Found undeclared constants in '{cfile}'. Attempting to auto-fix...")
                    temp_c_file = os.path.join(out_dir, "temp_" + file)
                    try:
                        with open(temp_c_file, 'w', encoding='utf-8') as f_temp:
                            f_temp.writelines(defines_to_add)
                            with open(cfile, 'r', encoding='utf-8') as f_orig:
                                f_temp.write(f_orig.read())

                        retry_cmd = ["gcc", "-Wall", "-Wextra", "-O2", "-D_GNU_SOURCE", "-pg", "-o", output_file, temp_c_file] + link_libs
                        retry_result = subprocess.run(retry_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')

                        if retry_result.returncode == 0:
                            print(f"Compile success (auto-fixed): {cfile} -> {output_file}")
                            defines_str = ''.join(defines_to_add).strip().replace('\n', ', ')
                            fix_msg = f"FIXED: {cfile} - Added defines: {defines_str}"
                            log_error(fix_msg)
                            total_compiled += 1
                            try_run(output_file, rel_path)
                        else:
                            msg = (
                                f"Compile failed (retry failed): {cfile}\n"
                                f"--- Original Error ---\n{result.stderr}\n"
                                f"--- Auto-fix attempt content ---\n{''.join(defines_to_add)}"
                                f"--- Retry Error ---\n{retry_result.stderr}\n"
                                f"{'-'*40}\n"
                            )
                            print(msg)
                            log_error(msg)
                    finally:
                        if os.path.exists(temp_c_file):
                            os.remove(temp_c_file)
                else:
                    msg = (
                        f"Compile failed: {cfile}\n"
                        f"--- gcc stderr ---\n{result.stderr}\n"
                        f"--- gcc stdout ---\n{result.stdout}\n"
                        f"{'-'*40}\n"
                    )
                    print(msg)
                    log_error(msg)

if __name__ == "__main__":
    compile_c_files()