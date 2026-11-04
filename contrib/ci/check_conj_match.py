#!/usr/bin/env python3
"""Check that a conjugate matched source yields a near-zero S[1,1].

Usage: check_conj_match.py <dataset>

The dataset is expected to originate from a netlist with a source of
impedance 1+j159.155 Ohm driving a series combination of 1 Ohm and 1 pF
at 1 GHz, i.e. the port impedance is the conjugate of the load.  Under
power-wave normalization the reflection must (nearly) vanish.
"""

import re
import sys

NUM = r"[+\-]?[0-9.]+(?:[eE][+\-]?[0-9]+)?"


def parse_value(line):
    m = re.fullmatch(
        rf"\s*({NUM})(?:([+\-])j({NUM}))?\s*", line)
    if not m:
        raise ValueError(f"cannot parse dataset value: {line!r}")
    real = float(m.group(1))
    imag = 0.0
    if m.group(2):
        imag = float(m.group(3))
        if m.group(2) == "-":
            imag = -imag
    return complex(real, imag)


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: check_conj_match.py <dataset>")
    txt = open(sys.argv[1]).read()
    m = re.search(r"<dep S\[1,1\][^>]*>\s*\n\s*(.*)", txt)
    if not m:
        sys.exit("no S[1,1] found in dataset")
    s11 = parse_value(m.group(1))
    if abs(s11) >= 1e-3:
        sys.exit(f"conjugate match failed: |S11| = {abs(s11):.3e} too large")
    print(f"conjugate match |S11| = {abs(s11):.3e} OK")


if __name__ == "__main__":
    main()
