"""Minimal reader for the DCD trajectories written by NAMD (CHARMM format, little-endian).

A DCD file is a sequence of Fortran records, each framed by its length in bytes:
  header (number of frames, first step, save frequency, unit-cell flag),
  a title, the number of atoms,
  then for every frame: the unit cell (6 doubles) if the flag is set, and the
  X, Y and Z coordinates as three separate records of float32.
"""
import struct

import numpy as np


def read_dcd(path):
    """Returns natoms, nframes, first step, save frequency, coordinates (frames, atoms, 3) and cells."""
    data = open(path, "rb").read()
    pos = 0

    def record():
        nonlocal pos
        length = struct.unpack("<i", data[pos:pos + 4])[0]
        body = data[pos + 4:pos + 4 + length]
        pos += length + 8                       # skip the closing length marker too
        return body

    header = record()
    nset, istart, nsavc = struct.unpack("<3i", header[4:16])
    has_cell = struct.unpack("<i", header[40:44])[0]
    record()                                    # title
    natoms = struct.unpack("<i", record())[0]
    frames, cells = [], []
    while pos < len(data):
        if has_cell:
            cells.append(np.frombuffer(record(), "<f8"))
        xyz = [np.frombuffer(record(), "<f4") for _ in range(3)]
        frames.append(np.stack(xyz, axis=1))
    return natoms, nset, istart, nsavc, np.array(frames), np.array(cells)
