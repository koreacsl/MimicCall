#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$ROOT_DIR/src"
TBL2_DIR="$SRC_DIR/tbl2"
CLAIM_DIR="$ROOT_DIR/claim"
mkdir -p "$CLAIM_DIR"

python3 -m pip install --upgrade pip

echo "Upgrading numpy and python-dateutil to compatible versions..."
python3 -m pip install --upgrade numpy python-dateutil

echo "Installing required libraries: scikit-learn, adjustText, matplotlib, seaborn, pandas"
python3 -m pip install scikit-learn adjustText matplotlib seaborn pandas

python3 -u "$SRC_DIR/fig3_4.py"

python3 -u "$SRC_DIR/fig5.py"

python3 -u "$SRC_DIR/tbl3.py" --include sendmsg --exclude sendto
python3 -u "$SRC_DIR/tbl3.py" --include socket --exclude socketpair
python3 -u "$SRC_DIR/tbl3.py" --include writev --exclude sendmsg

if [ -d "$TBL2_DIR" ]; then
    for py in "$TBL2_DIR"/*.py; do
    [ -e "$py" ] || continue
    base="$(basename "$py" .py)"
    claim_file="$CLAIM_DIR/tbl2_${base}.txt"
    echo "Running $base -> $claim_file"
    python3 -u "$py" | grep -E "^\[+\].*(Min|Max) vulnerable functions per filter" > "$claim_file" || true
    done
fi

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$ROOT_DIR/src"
TBL2_DIR="$SRC_DIR/tbl2"
CLAIM_DIR="$ROOT_DIR/claim"
mkdir -p "$CLAIM_DIR"

python3 -u "$SRC_DIR/fig3_4.py"
python3 -u "$SRC_DIR/fig5.py"
python3 -u "$SRC_DIR/tbl3.py" --include sendmsg --exclude sendto
python3 -u "$SRC_DIR/tbl3.py" --include socket --exclude socketpair
python3 -u "$SRC_DIR/tbl3.py" --include writev --exclude sendmsg

if [ -d "$TBL2_DIR" ]; then
    for py in "$TBL2_DIR"/*.py; do
    [ -e "$py" ] || continue
    base="$(basename "$py" .py)"
    claim_file="$CLAIM_DIR/tbl2_${base}.txt"

    echo "Running $base -> $claim_file" >&2

    output="$(python3 -u "$py" 2>&1 || true)"

    matches="$(printf "%s\n" "$output" | grep -E -i 'min vulnerable functions per filter|max vulnerable functions per filter' || true)"

    if [ -n "$matches" ]; then
        printf "%s\n" "%s\n" "$matches" > "$claim_file"
    else
        matches2="$(printf "%s\n" "$output" | grep -E -i 'vulnerable functions per filter' || true)"
        if [ -n "$matches2" ]; then
        printf "%s\n" "%s\n" "$matches2" > "$claim_file"
        else
        printf "=== NO min/max line found in output ===\n\nFull output:\n\n%s\n" "$output" > "$claim_file"
        fi
    fi
    done
else
    echo "Warning: tbl2 directory not found at $TBL2_DIR" >&2
fi
