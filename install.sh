#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Helper function for error handling ---
# Prints an error message and exits.
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# --- Main Script ---

echo "Updating package lists..."
sudo apt-get update || error_exit "Failed to update package lists."

echo "Installing base dependencies via apt..."
sudo apt-get install -y \
    build-essential \
    git \
    pkg-config \
    libdw-dev \
    libelf-dev \
    libncurses5-dev \
    libcap-dev \
    python3-dev \
    libluajit-5.1-dev \
    libjson-c-dev \
    libpython2.7-dev \
    libcapstone-dev \
    libunwind-dev || error_exit "Failed to install base dependencies."

echo "--------------------------------------------------"
echo "Starting tracing tool installation."
echo "--------------------------------------------------"

# Install libtraceevent
# Remove the directory if it exists to prevent a clone error.
if [ -d "libtraceevent" ]; then
    echo "'libtraceevent' directory found. Removing for a clean installation."
    rm -rf libtraceevent
fi

echo "Cloning and installing libtraceevent..."
git clone https://git.kernel.org/pub/scm/libs/libtrace/libtraceevent.git || error_exit "Failed to clone libtraceevent."
cd libtraceevent
make || error_exit "Failed to build (make) libtraceevent."
sudo make install || error_exit "Failed to install (make install) libtraceevent."
cd ..

# Install uftrace
# Remove the directory if it exists.
if [ -d "uftrace" ]; then
    echo "'uftrace' directory found. Removing for a clean installation."
    rm -rf uftrace
fi

echo "Cloning and installing uftrace..."
git clone https://github.com/namhyung/uftrace.git || error_exit "Failed to clone uftrace."
cd uftrace
./configure || error_exit "Failed to configure uftrace."
make || error_exit "Failed to build (make) uftrace."
sudo make install || error_exit "Failed to install (make install) uftrace."

# Update library cache
sudo ldconfig

echo "--------------------------------------------------"
echo "Tracing tool installation with all features is complete."
echo "--------------------------------------------------"

echo "--------------------------------------------------"
echo "Generating test codes in tool/syscall..."
echo "--------------------------------------------------"

cd ..

if [ -d "tool/syscall" ]; then
    for script in $(find tool/syscall -name "*.py"); do
        echo "Executing: python3 $script"
        python3 "$script" || echo "Warning: '$script' encountered an issue during execution."
    done
else
    echo "Warning: 'tool/syscall' directory not found. Skipping script execution."
fi

echo "--------------------------------------------------"
echo "Compiling test codes in tool/compile..."
echo "--------------------------------------------------"
if [ -f "tool/compile.py" ]; then
    echo "Executing: python3 tool/compile.py"
    python3 tool/compile.py || echo "Warning: 'tool/compile.py' encountered an issue during execution."
else
    echo "Warning: 'tool/compile.py' not found. Skipping compilation."
fi

# Clean up generated test files
rm -f tool/file tool/testfile tool/testfile_in tool/testfile_out

echo "--------------------------------------------------"
echo "Tracing test codes with tool/trace.py..."
echo "--------------------------------------------------"
if [ -f "tool/trace.py" ]; then
    echo "Executing: python3 tool/trace.py"
    python3 tool/trace.py || echo "Warning: 'tool/trace.py' encountered an issue during execution."
else
    echo "Warning: 'tool/trace.py' not found. Skipping tracing."
fi

echo "--------------------------------------------------"
echo "Generating csvs with tool/trace2csv.py..."
echo "--------------------------------------------------"
if [ -f "tool/trace2csv.py" ]; then
    echo "Executing: python3 tool/trace2csv.py"
    python3 tool/trace2csv.py || echo "Warning: 'tool/trace2csv.py' encountered an issue during execution."
else
    echo "Warning: 'tool/trace2csv.py' not found. Skipping csv generation."
fi

echo "--------------------------------------------------"
echo "Installation script finished successfully."
echo "--------------------------------------------------"