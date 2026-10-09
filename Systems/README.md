# Systems

Structures and GROMACS input used to derive and test the MINFF parameters. The
45 numbered systems here are the ones the tailored (TMINFF) Lennard-Jones
parameters were optimised against, and they double as test cases for checking
that a MINFF build reproduces the expected unit cell metrics.

## Contents

| Path | What it holds |
|---|---|
| `topol.top` | Template GROMACS topology |
| `conf.mdp` | MD settings used for the production runs |
| `powerspectra.mdp` | MD settings for vibrational power spectra |
| `itp/` | 45 MINFF topologies, `min1.itp` to `min45.itp` |
| `conf/` | 45 matching supercell configurations, `preem1` to `preem45` |
| `UC_conf/` | 34 single unit cells, named by mineral |
| `UC_conf/zeolites/` | 13 zeolite frameworks, named by framework code |

## Numbering

`min<N>.itp` and `preem<N>.*` share one index, and that index is the mineral
number in the table in the top-level [README.md](../README.md). So `min5` is
brucite, `min7` quartz, `min19` hematite, `min34` rutile, and so on. The atom
types in each `.itp` follow from that: `min5` contains `Mgh`, `Oh` and `H`;
`min19` contains `Feo3` and `Ob`.

Two indices have no mineral name in that table, and both are worth knowing
about. `preem13.gro` is byte-identical to `preem7.gro`, so system 13 is a second
copy of quartz rather than a distinct mineral; it is the only duplicated
structure in `conf/`. System 22 is a distinct structure with `Feo3`, `Fet2` and
`Obt`, an Fe3O4-like composition, but it is unnamed in the mineral list and has
no corresponding TMINFF parameter block.

## Running one of these systems

`topol.top` is a template rather than a ready-to-run topology. It sets the
angle force constant and includes the force field, the ion and water
definitions, and a mineral topology under the generic name `min.itp`:

```
#define KANGLE 500.00

#include "min.ff/forcefield.itp"
#include "min.ff/ions.itp"
#include "min.ff/opc3.itp"
#include "min.itp"
```

To use it, copy the system you want to `min.itp`, put a copy of `min.ff/`
alongside, and add `[ system ]` and `[ molecules ]` sections. For kaolinite,
which is system 1:

```bash
cp Systems/itp/min1.itp      min.itp
cp Systems/conf/preem1.gro   conf.gro
cp -r min.ff .
cp Systems/topol.top .
printf '\n[ system ]\nMINFF test\n\n[ molecules ]\nMIN   1\n' >> topol.top
```

Then edit `topol.top` to include `min.ff/forcefield_tminff.itp` instead of
`min.ff/forcefield.itp`, and edit the first line of your `.mdp` to read:

```
define = -DKaolinite -DMINFF_k500 -DOPC3
```

Then build it:

```bash
gmx grompp -f conf.mdp -c conf.gro -p topol.top -o run.tpr
```

That builds with no warnings. Pick a different system by changing all three of
the index, the mineral define and the `min.itp` you copy.

Minerals with isomorphic substitution carry a permanent layer charge and will
not run as bare slabs. System 27, montmorillonite, has a net charge of -48 e,
so grompp stops with a net-charge warning under Ewald electrostatics until
counterions are added. Use `gmx genion`, or one of the ready-made examples in
the [atom](https://github.com/mholmboe/atom) toolbox under
`ATOM_scripts_lecture/MINFF`, which ship solvated and counterion-balanced
montmorillonite systems.

`KANGLE` in `topol.top` and the `-D` flags in the `.mdp` have to agree on the
angle force constant. The `.itp` files carry `KANGLE` symbolically in every
angle line, so setting it to 500.00 means pairing it with `-DMINFF_k500`.

For the general parameters, include `min.ff/forcefield.itp` as above and select
with `-DMINFF_k500`. For the tailored ones, include
`min.ff/forcefield_tminff.itp` instead and select with the mineral name as well,
`-DMontmorillonite -DMINFF_k500`. Both defines are required for a tailored set.

Note that `conf.mdp` as shipped has `define = -DOPC3` only, so it selects a
water model but no mineral parameters. Add the parameter-set flags to that line
before running.

## What is in each file type

**`itp/min<N>.itp`** are MINFF topologies written by the `atom` MATLAB toolbox.
The moleculetype is always called `MIN`. Angles carry their equilibrium value
and the `KANGLE` symbol inline, so they do not depend on `[ angletypes ]`.
Bonds carry no parameters at all, only the atom indices and function type, with
the distance in a trailing comment, so they are resolved from `[ bondtypes ]`
in `ffbonded.itp` at run time.

**`conf/preem<N>.gro`** are the matching supercells, from 1140 to 5088 atoms. Each comes with a `.log` recording the box matrix, the cell
parameters *a*, *b*, *c*, α, β, γ and the volume, and a `.n2t` listing the atom
name to atom type mapping with coordination environments and neighbour
distances, for use with the patched `gmx x2top` in [x2top_hack](../x2top_hack).

**`UC_conf/`** holds single unit cells as PDB, one per mineral, with the same
`.log` and `.n2t` companions. The number in each filename is the Global
Instability Index from a bond-valence analysis of that structure, a measure of
how well the bond-valence sums match formal valences; lower is better. Values
here run from 0.0027 for brucite to 0.196 for akdalaite. `Maghemite_GII_0.138`
is the only structure without an `.n2t`.

**`UC_conf/zeolites/`** holds 13 framework structures as PDB with `.n2t`
files, and no `.log` companions. Twelve are named by their IZA framework code,
ABW, ANA, CHA, ETR, EUO, EZT, FAU, FER, HEU, MOR, PHI and SOD. The thirteenth
is named ZSM-5, which is a trade name rather than a framework code; its IZA
code is MFI.

## Provenance

The crystallographic source for each mineral is cited in the reference table at
the bottom of the top-level [README.md](../README.md). The structures were
processed with the [atom](https://github.com/mholmboe/atom) MATLAB toolbox,
which assigned the MINFF atom types and charges and wrote the topologies.
