#!/usr/bin/env python3
"""Generate a MINFF atomname2type.n2t file for gmx x2top from a PDB unit cell.

Standalone (Python 3 standard library only). The script

1. reads the CRYST1 record and the atom coordinates of a PDB file,
2. finds the bonded neighbours of every atom with a triclinic periodic
   minimum-image search (so bonds across the cell boundary are counted),
   (atoms duplicated across the cell boundary are removed first),
3. assigns MINFF atomtypes from element, coordination number and the
   neighbour elements, and
4. computes the cation charges from a fixed table and the oxygen charges
   from the charge-smearing equation of Lammers et al. 2017
   (doi:10.1016/j.jcis.2016.11.084),

       q_O = -2 + sum_M (q_nominal(M) - q(M)) / CN(M),

   where the sum runs over the bonded cations and hydrogens M, and H has
   q_nominal = 1 and CN = 1.

The atom names in the PDB file are not used. They are partly generic ("O",
"Al", "Fe") and not reliable across the unit cells. Fe(II)/Fe(III) is decided
from charge neutrality of the cell (nominal valences), which fails for mixed
valence cells; the script then picks Fe(III) when the average valence is >= 2.5
and prints a warning.

Usage:
    python3 make_n2t.py structure.pdb [more.pdb ...] [-o outdir]

Writes <name>.n2t next to each input (or in outdir). Pass the file to
`gmx x2top -n2t <name>.n2t`. Pass -smear to x2top to let it recompute the
oxygen charges per site, in which case the O charges below are only a fallback.

Atoms that end up without a cation or hydrogen neighbour (for instance water
oxygens in a zeolite cell) are skipped and reported on stderr.
"""
import argparse
import math
import os
import sys
from collections import defaultdict

MASS = {"H": 1.00794, "O": 15.9994, "Si": 28.0855, "Al": 26.9815, "Mg": 24.305,
        "Ca": 40.078, "Fe": 55.845, "Li": 6.94, "Ti": 47.867, "F": 18.9984}
# Nominal valence (for charge neutrality and the smearing equation)
VALENCE = {"H": 1, "Li": 1, "Mg": 2, "Ca": 2, "Al": 3, "Si": 4, "Ti": 4}
# Maximum bond length in Angstrom for centre-atom (cation, H) to ligand (O, F)
CUTOFF = {("H", "O"): 1.25, ("Si", "O"): 1.95, ("Al", "O"): 2.30,
          ("Mg", "O"): 2.45, ("Mg", "F"): 2.30, ("Ca", "O"): 2.70,
          ("Ca", "F"): 2.70, ("Fe", "O"): 2.45, ("Ti", "O"): 2.35,
          ("Li", "O"): 2.45}
CATIONS = ("Si", "Al", "Mg", "Ca", "Fe", "Li", "Ti")
ELEMENTS = {"H", "O", "F", "Li", "Mg", "Al", "Si", "Ca", "Ti", "Fe"}


def read_pdb(path):
    cell, atoms = None, []
    with open(path) as fh:
        for line in fh:
            if line.startswith("CRYST1"):
                cell = [float(x) for x in line[6:54].split()]
            elif line.startswith(("ATOM", "HETATM")):
                el = line[76:78].strip().capitalize()
                if el not in ELEMENTS:
                    el = "".join(c for c in line[12:16].strip() if c.isalpha())[:2].capitalize()
                    if el not in ELEMENTS:
                        el = el[:1]
                if el not in ELEMENTS:
                    raise ValueError("%s: unknown element in line: %s" % (path, line.strip()))
                atoms.append((el, [float(line[30:38]), float(line[38:46]), float(line[46:54])]))
    if cell is None or len(cell) != 6:
        raise ValueError("%s: no CRYST1 record" % path)
    return cell, atoms


def lattice(cell):
    a, b, c, al, be, ga = cell
    al, be, ga = (math.radians(x) for x in (al, be, ga))
    cx = c * math.cos(be)
    cy = c * (math.cos(al) - math.cos(be) * math.cos(ga)) / math.sin(ga)
    cz = math.sqrt(max(c * c - cx * cx - cy * cy, 0.0))
    return [[a, 0.0, 0.0], [b * math.cos(ga), b * math.sin(ga), 0.0], [cx, cy, cz]]


def inverse3(m):
    (a, b, c), (d, e, f), (g, h, i) = m
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    return [[(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
            [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
            [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det]]


def dedupe(cell, atoms, tol=0.5):
    """Drop atoms that sit within tol Angstrom of an earlier atom of the same
    element once periodic images are considered (a common export artefact:
    atoms on a cell face written once for each face)."""
    L = lattice(cell)
    Linv = inverse3(L)
    frac = [[sum(p[k] * Linv[k][j] for k in range(3)) for j in range(3)] for _, p in atoms]
    keep = []
    for i, (e, _) in enumerate(atoms):
        for j in keep:
            if atoms[j][0] != e:
                continue
            d = [frac[i][k] - frac[j][k] for k in range(3)]
            d = [x - round(x) for x in d]
            if math.sqrt(sum(sum(d[r] * L[r][c] for r in range(3)) ** 2 for c in range(3))) < tol:
                break
        else:
            keep.append(i)
    return [atoms[i] for i in keep]


def find_bonds(cell, atoms):
    """Return nbrs[i] = list of (j, distance in Angstrom) for centre atoms i."""
    L = lattice(cell)
    Linv = inverse3(L)
    frac = [[sum(p[k] * Linv[k][j] for k in range(3)) for j in range(3)] for _, p in atoms]
    ncell = 2 if min(cell[:3]) < 7.0 else 1
    shifts = [(i, j, k) for i in range(-ncell, ncell + 1) for j in range(-ncell, ncell + 1)
              for k in range(-ncell, ncell + 1)]
    cart_shift = [tuple(sum(s[r] * L[r][c] for r in range(3)) for c in range(3)) for s in shifts]
    ligands = [i for i, (e, _) in enumerate(atoms) if e in ("O", "F")]
    nbrs = defaultdict(list)
    for i, (ei, _) in enumerate(atoms):
        if ei in ("O", "F"):
            continue
        for j in ligands:
            cut = CUTOFF.get((ei, atoms[j][0]))
            if cut is None:
                continue
            d = [frac[j][k] - frac[i][k] for k in range(3)]
            d = [x - round(x) for x in d]
            base = [sum(d[r] * L[r][c] for r in range(3)) for c in range(3)]
            for sc in cart_shift:
                r = math.sqrt(sum((base[c] + sc[c]) ** 2 for c in range(3)))
                if r <= cut:
                    nbrs[i].append((j, r))
    for i in list(nbrs):
        if atoms[i][0] == "H":      # a hydrogen bonds to its nearest oxygen only
            nbrs[i] = [min(nbrs[i], key=lambda t: t[1])]
    return nbrs


def fe_valence(atoms):
    cnt = defaultdict(int)
    for e, _ in atoms:
        cnt[e] += 1
    if not cnt["Fe"]:
        return 3
    pos = sum(VALENCE[e] * n for e, n in cnt.items() if e in VALENCE)
    ox = (2 * cnt["O"] + cnt["F"] - pos) / cnt["Fe"]
    if abs(ox - round(ox)) > 0.05:
        print("  warning: mixed-valence Fe (average +%.2f); Fe(III) assumed for Fe >= +2.5" % ox,
              file=sys.stderr)
    return 3 if ox >= 2.5 else 2


def assign(atoms, nbrs, fe_ox):
    """Return types, charges, coordination (lists, None for skipped atoms)."""
    n = len(atoms)
    # ligand -> bonded centre atoms
    lig = defaultdict(list)
    for i, lst in nbrs.items():
        for j, r in lst:
            lig[j].append((i, r))
    types, charge, cn = [None] * n, [None] * n, [0] * n
    for i, lst in nbrs.items():
        cn[i] = len(lst)
    for i, (e, _) in enumerate(atoms):
        if e in ("O", "F"):
            cn[i] = len(lig[i])
    # cations and hydrogen
    for i, (e, _) in enumerate(atoms):
        if e in ("O", "F") or not nbrs.get(i):
            continue
        ligs = {atoms[j][0] for j, _ in nbrs[i]}
        hyd = any(any(atoms[k][0] == "H" for k, _ in lig[j]) for j, _ in nbrs[i])
        c = cn[i]
        if e == "H":
            types[i], charge[i] = "H", 0.4
        elif e == "Si":
            types[i], charge[i] = "Sit", 1.884
        elif e == "Al":
            types[i], charge[i] = {6: "Alo", 4: "Alt", 5: "Ale"}.get(c, "Alo"), 1.782
        elif e == "Mg":
            oh = "F" in ligs or hyd
            types[i], charge[i] = ("Mgh", 1.74) if oh else ("Mgo", 1.562)
        elif e == "Ca":
            oh = "F" in ligs or hyd
            types[i] = "Cah" if oh else "Cao"
            charge[i] = 1.52 if "F" in ligs else 1.66
        elif e == "Fe":
            sfx = {6: "o", 4: "t", 5: "e"}.get(c, "o")
            types[i] = "Fe%s%d" % (sfx, fe_ox)
            charge[i] = 1.5 if fe_ox == 3 else 1.184
        elif e == "Li":
            types[i], charge[i] = "Lio", 0.86
        elif e == "Ti":
            types[i], charge[i] = "Tio", 2.48
    for i, (e, _) in enumerate(atoms):
        if e == "F" and lig[i]:
            mg = any(atoms[k][0] == "Mg" for k, _ in lig[i])
            types[i], charge[i] = "Fs", (-0.87 if mg else -0.76)
    # oxygen: type from the environment, charge from the smearing equation
    for i, (e, _) in enumerate(atoms):
        if e != "O" or not lig[i]:
            continue
        nb = [atoms[k][0] for k, _ in lig[i]]
        metals = [k for k, _ in lig[i] if atoms[k][0] != "H"]
        mel = {atoms[k][0] for k in metals}
        if not metals:
            continue
        if "H" in nb:
            t = "Oh"
        elif "Li" in mel:
            t = "Oli"
        elif "Si" in mel and len(mel) > 1:
            t = "Op"
        elif mel == {"Fe"} and all(types[k] == "Feo2" for k in metals):
            t = "Op"
        elif len(nb) == 4 and any(cn[k] == 4 for k in metals):
            t = "Obt"
        else:
            t = "Ob"
        q = -2.0
        for k, _ in lig[i]:
            ek = atoms[k][0]
            nom = 1.0 if ek == "H" else (fe_ox if ek == "Fe" else VALENCE[ek])
            q += (nom - charge[k]) / cn[k]
        types[i], charge[i] = t, round(q, 4)
    return types, charge, cn


def write_n2t(path, name, atoms, nbrs, types, charge, cn):
    lig = defaultdict(list)
    for i, lst in nbrs.items():
        for j, r in lst:
            lig[j].append((i, r))
    groups = defaultdict(list)
    for i, (e, _) in enumerate(atoms):
        if types[i] is None:
            continue
        nb = nbrs[i] if i in nbrs else lig[i]
        pairs = sorted((atoms[j][0], r / 10.0) for j, r in nb)
        key = (e, types[i], cn[i], round(charge[i], 4), tuple(p[0] for p in pairs))
        groups[key].append(pairs)
    order = {"H": 0, "O": 1, "F": 2}
    keys = sorted(groups, key=lambda k: (order.get(k[0], 3), k[0], k[1], k[2]))
    seen = {}
    lines = ["; atomname2type.n2t for %s, generated by make_n2t.py" % name,
             "; Columns: Element  AtomType  Charge  Mass[u]  CN  [NeighborElement  Distance(nm)]",
             "; Oxygen charges from the charge-smearing equation of Lammers et al. 2017 "
             "(doi:10.1016/j.jcis.2016.11.084);",
             "; they are only a fallback when gmx x2top is run with -smear.",
             "; Neighbour distances are group averages over the unit cell (nm); x2top uses them "
             "as a +-10% window."]
    for key in keys:
        e, t, c, q, nel = key
        members = groups[key]
        avg = [sum(m[p][1] for m in members) / len(members) for p in range(len(nel))]
        line = "%-2s %-4s%22.6f%11.5f  %d" % (e, t, q, MASS[e], c)
        for el, d in zip(nel, avg):
            line += "  %-2s %.3f" % (el, d)
        lines.append(line)
        sig = (e, c, nel)
        if sig in seen and seen[sig] != (t, q):
            print("  warning: %s: %s and %s share element, CN and neighbours; x2top will use "
                  "the first" % (name, seen[sig][0], t), file=sys.stderr)
        seen.setdefault(sig, (t, q))
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pdb", nargs="+")
    ap.add_argument("-o", "--outdir", help="output directory (default: next to each PDB)")
    args = ap.parse_args()
    for path in args.pdb:
        name = os.path.splitext(os.path.basename(path))[0]
        cell, atoms = read_pdb(path)
        n0 = len(atoms)
        atoms = dedupe(cell, atoms)
        if len(atoms) != n0:
            print("  %s: removed %d atoms duplicated across the cell boundary"
                  % (name, n0 - len(atoms)), file=sys.stderr)
        nbrs = find_bonds(cell, atoms)
        types, charge, cn = assign(atoms, nbrs, fe_valence(atoms))
        skipped = sum(1 for t in types if t is None)
        if skipped:
            print("  %s: %d of %d atoms have no bonded cation/H and were skipped"
                  % (name, skipped, len(atoms)), file=sys.stderr)
        net = sum(q for q in charge if q is not None)
        if abs(net) > 0.02 * len(atoms) ** 0.5:
            print("  %s: net cell charge %+.3f e" % (name, net), file=sys.stderr)
        outdir = args.outdir or os.path.dirname(os.path.abspath(path))
        out = os.path.join(outdir, name + ".n2t")
        write_n2t(out, name, atoms, nbrs, types, charge, cn)
        print("wrote", out)


if __name__ == "__main__":
    main()
