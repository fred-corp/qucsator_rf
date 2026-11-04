#!/usr/bin/env python3
"""Check the S[1,1] of a complex impedance power source dataset.

Usage: check_s11.py <dataset>

Expected dataset: a Pac with Z=49+j24 Ohm driving a 50 Ohm load.
The power-wave reflection is (ZL - conj(z0)) / (ZL + z0); the value is
compared against the closed-form result with a small tolerance since
floating point results differ in their low bits between platforms
(FMA contraction etc.).
"""

import re
import sys

NUM = r"[+\-]?[0-9.]+(?:[eE][+\-]?[0-9]+)?"

EXPECTED = complex(0.0650477016478751, 0.22665510263081817)
TOLERANCE = 1e-6


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
        sys.exit("usage: check_s11.py <dataset>")
    txt = open(sys.argv[1]).read()
    m = re.search(r"<dep S\[1,1\][^>]*>\s*\n\s*(.*)", txt)
    if not m:
        sys.exit("no S[1,1] found in dataset")
    s11 = parse_value(m.group(1))
    if abs(s11 - EXPECTED) > TOLERANCE * max(1.0, abs(EXPECTED)):
        sys.exit(f"S[1,1] mismatch: got {s11}, expected {EXPECTED}")
    print(f"complex impedance S[1,1] = {s11:.6f} OK")


if __name__ == "__main__":
    main()
