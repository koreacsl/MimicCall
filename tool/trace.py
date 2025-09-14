import os
import subprocess
import time

def process_binaries(exe_folder, uftrace_folder, error_log_file):
    os.makedirs(uftrace_folder, exist_ok=True)

    binary_folders = [
        os.path.join(exe_folder, d)
        for d in os.listdir(exe_folder)
        if os.path.isdir(os.path.join(exe_folder, d))
    ]

    with open(error_log_file, "w") as error_log:
        for binary_folder in binary_folders:
            system_call_folder = os.path.basename(binary_folder)
            output_folder = os.path.join(uftrace_folder, system_call_folder)
            os.makedirs(output_folder, exist_ok=True)

            for binary in os.listdir(binary_folder):
                binary_path = os.path.join(binary_folder, binary)
                
                if os.path.isfile(binary_path) and os.access(binary_path, os.X_OK):
                    trace_dir = os.path.join(output_folder, f"{binary}_trace")
                    output_graph_file = os.path.join(output_folder, f"{binary}_graph.txt")

                    if os.path.exists(output_graph_file):
                        continue

                    os.makedirs(trace_dir, exist_ok=True)
                    print(f"Recording trace for {binary}...")

                    start_time = time.time()
                    try:
                        subprocess.run([
                            "sudo", "uftrace", "record",
                            "-K", "20",
                            "-d", trace_dir,
                            binary_path
                        ], check=True, timeout=5)

                        end_time = time.time()
                        duration = end_time - start_time
                        print(f"[{binary}] Trace end time: {end_time:.2f} seconds since epoch (duration: {duration:.2f}s)")

                        with open(output_graph_file, "w") as f:
                            subprocess.run([
                                "sudo", "uftrace", "graph",
                                "-d", trace_dir
                            ], stdout=f, check=True)

                    except subprocess.TimeoutExpired:
                        error_log.write(f"{binary_path}: timeout after 5s\n")

                    except subprocess.CalledProcessError as e:
                        error_log.write(f"{binary_path}: {e}\n")

                    if os.path.exists(trace_dir):
                        subprocess.run(["sudo", "rm", "-rf", trace_dir], check=True)
                    if os.path.exists(trace_dir + ".old"):
                        subprocess.run(["sudo", "rm", "-rf", trace_dir + ".old"], check=True)

if __name__ == "__main__":
    exe_folder = "./tool/exe"
    trace_folder = "./tool/trace"
    error_log_file = "./tool/trace_runtime_errors.log"
    process_binaries(exe_folder, trace_folder, error_log_file)