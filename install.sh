#!/bin/bash

set -e

sudo apt-get update

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
    libunwind-dev

echo "--------------------------------------------------"
echo "tracing tool installation"
echo "--------------------------------------------------"

git clone https://git.kernel.org/pub/scm/libs/libtrace/libtraceevent.git
cd libtraceevent
make
sudo make install
cd ..

if [ -d "uftrace" ]; then
    rm -rf uftrace
fi
git clone https://github.com/namhyung/uftrace.git
cd uftrace
./configure
make
sudo make install

sudo ldconfig

echo "--------------------------------------------------"
echo "tracing tool installation with all features is complete"
echo "--------------------------------------------------"

echo "--------------------------------------------------"
echo "Generating test codes in tool/syscall..."
echo "--------------------------------------------------"

if [ -d "tool/syscall" ]; then
    for script in $(find tool/syscall -name "*.py"); do
        echo "Executing: python3 $script"
        python3 "$script"
    done
else
    echo "Warning: 'tool/syscall' directory not found. Skipping script execution."
fi

echo "--------------------------------------------------"
echo "Compiling test codes in tool/compile..."
echo "--------------------------------------------------"
if [ -f "tool/compile.py" ]; then
    echo "Executing: python3 tool/compile.py"
    python3 tool/compile.py
else
    echo "Warning: 'tool/compile.py' not found. Skipping script execution."
fi
rm -f tool/file
rm -f tool/testfile
rm -f tool/testfile_in
rm -f tool/testfile_out

echo "--------------------------------------------------"
echo "Tracing test codes tool/trace.py..."
echo "--------------------------------------------------"
if [ -f "tool/trace.py" ]; then
    echo "Executing: python3 tool/trace.py"
    python3 tool/trace.py
else
    echo "Warning: 'tool/trace.py' not found. Skipping script execution."
fi

echo "--------------------------------------------------"
echo "Generating csvs tool/trace2csv.py..."
echo "--------------------------------------------------"
if [ -f "tool/trace2csv.py" ]; then
    echo "Executing: python3 tool/trace2csv.py"
    python3 tool/trace2csv.py
else
    echo "Warning: 'tool/trace2csv.py' not found. Skipping script execution."
fi