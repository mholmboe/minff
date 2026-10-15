# Setup MINFF topologies with Gromacs `gmx x2top`

This is a modified version of x2top, now ported to **GROMACS 2026.4** (`src/gromacs/gmxpreprocess/x2top.cpp`, `nm2type.cpp`, `nm2type.h`; the earlier 2025.3 hack is in the git history). A reviewable, backward-compatible patch series for the official GROMACS release is in preparation, so the features may become part of stock `gmx x2top`. MINFF is described in Holmboe, Lavauzelle and Swai, arXiv preprint (2026), doi:10.48550/arXiv.2610.18220. It has been tailored to generate MINFF topology files for Gromacs thanks to handling of bonds and angles across the PBC (-pbc yes) and the addition of new flags and output format. Specifically, it can be used to set the bond (-kb, -dH, and -dM) and angle (-kt, -ktH and -aH) constants explicitly, and write them in the simpler MINFF format instead of the OPLS/aa formatting style for [ bonds ] and [ angles ] sections in the .top/.itp file. Custom .n2t files can also be used with a -n2t flag, and -smear lets x2top compute the oxygen charges itself rather than reading them from the .n2t file. Note that the [**Systems/conf**](https://github.com/mholmboe/minff/tree/main/Systems/conf) directory contains a bunch of .n2t files for the different structures (numbered 1-45) used in training MINFF. 

Overall, the key changes to the native x2top.cpp are:

- **MINFF-aware help text** – the command-line help and man page now describe the MINFF-specific output format, default force constants, and the `min`/`minff` force-field selectors.
- **Option descriptions** – the `-ff`, `-n2t`, `-name`, `-kb`, `-kt`, and `-ktH` option blurbs document the MINFF behaviour so the guidance appears both in `gmx help x2top` and generated manuals. Note that with -n2t a custom .n2t file can be used.
- **Default handling** – internally, the code already applied MINFF defaults (bond distance printing, charge-group collapse, etc.); the documentation now matches that runtime behaviour.
- **Hydrogen-specific overrides** – new `-dH` (bond distance) and `-aH` (angle) flags let you override values for interactions involving hydrogens. Providing either flag automatically switches `[ bonds ]` to the explicit MINFF format (distance + force constant), defaulting the constant to 441050 kJ mol⁻¹ nm⁻² when `-kb` is omitted.
- **Hydrogen detection** – hydrogens are recognised from the n2t mass (< 2.5 u), else the PDB element column, else the atom name, so a hydroxyl hydrogen named `Ho` is treated as hydrogen, not holmium. `-ktH` is unset by default for other force fields and 110 for MINFF.
- **Oxygen charge smearing** – `-smear` computes the oxygen charges per site from the charge-smearing equation of Lammers et al. 2017 (doi:10.1016/j.jcis.2016.11.084) instead of reading them from the charge column of the `.n2t` file. This is the same scheme the [**atom**](https://github.com/mholmboe/atom) and [**atomipy**](https://github.com/mholmboe/atomipy) libraries use, and it is what gets the charges right at isomorphic substitution sites and terminating edge groups, where one tabulated charge per oxygen atomtype is not enough. Charges on the non-oxygen atomtypes are still read from the `.n2t` file as usual. With `-smear` the many per-environment oxygen entries in `min.ff/atomname2type.n2t`, such as the eight `Oh` and nine `Ob` variants, are no longer needed to carry charges; a single entry per oxygen atomtype is enough to establish the type.


No functional regressions were introduced—the program still honours charges read from a PDB/PDBQ file when you pass `-pdbq yes`, even when MINFF formatting is selected.

## .n2t files for the unit cell structures

Each unit cell in [**Systems/UC_conf**](https://github.com/mholmboe/minff/tree/main/Systems/UC_conf) (minerals and zeolites) comes with an `.n2t` file of the same basename, for instance `Kaolinite_GII_0.0487.n2t`, which can be passed directly to `-n2t`. They were generated from the PDB files with `make_n2t.py`, a standalone Python 3 script (standard library only, no atomipy needed) that finds the bonded neighbours with a periodic triclinic search, assigns the MINFF atomtypes from element, coordination number and neighbour elements, and computes the oxygen charges with the charge-smearing equation of Lammers et al. 2017. For the minerals that are also part of the training set, the generated files reproduce the corresponding `Systems/conf/preem*.n2t` files. No `.n2t` file is provided for the Maghemite cell (`Maghemite_GII_0.138.pdb`), since it is Fe24O32, i.e. magnetite stoichiometry with mixed Fe(II)/Fe(III) (average +2.67), and cannot be made charge neutral with a single Fe(III) charge. Use `Systems/conf/preem12.n2t` or a corrected vacancy-containing cell instead. To regenerate or to make a file for a new structure:

```bash
python3 make_n2t.py ../Systems/UC_conf/Kaolinite_GII_0.0487.pdb
```

Some points to be aware of:

- The atom names in the PDB files are ignored, since several are generic (`O`, `Al`, `Fe`). Fe(II) vs. Fe(III) is taken from charge neutrality of the cell; for a mixed-valence cell the script assumes Fe(III) when the average valence is at least +2.5 and prints a warning.
- Nine zeolite PDB files (ABW, EUO, EZT, FAU, FER, HEU, MOR, PHI, SOD) used to contain atoms written twice on opposite cell faces; these duplicates have been removed, and every zeolite cell is now SiO2. The script still drops atoms closer than 0.5 Å to an earlier atom of the same element under periodic boundary conditions, so PDB files exported with the same artefact can be used as they are.
- The oxygen charges in the files are a fallback. Run `gmx x2top` with `-smear` to compute them per site.

## Installing the patched x2top tool in GROMACS

1. **Download and replace the old x2top.cpp** 
   - Download Gromacs as you normally would do..
   - Copy the modified version of x2top.cpp to gromacs-2026.4/src/gromacs/gmxpreprocess/, replacing the original `x2top.cpp`, `nm2type.cpp` and `nm2type.h` (all three are needed). Built and tested on 2026.4 (configure with `-DGMX_USE_LMFIT=NONE` if the bundled lmfit fails to link).
   - Copy the entire min.ff directory from this repo with all its forcefield files to gromacs-2026.4/share/top/. This can also be done after installation. Note that this directory comes with a generic example of a atomname2type.n2t file, which you can edit to reflect your structures atomtypes.

2. **Build and Install**:
   - Do a normal build and installation of Gromacs according to the Gromacs installation
  
3. **Test the installation**:
   - Run gmx x2top -h. Does the instructions mention minff? If so, it likely works! If it does not work, make sure your installation protocoll does not involve downloadng a new Gromacs distribution (.tar) bundle, since it would overwrite the new and patched `src/gromacs/gmxpreprocess/x2top.cpp` file.
     

## Using `gmx x2top` with a Custom `atomname2type.n2t`

1. **Prepare your coordinate file** (e.g. `structure.gro | .pdb`). If you store charges in the B-factor column, enable them with `-pdbq yes` when you run the tool.

2. **Create or edit the name-to-type mapping** (`atomname2type.n2t`). Each line maps an atom name to an element, bond partners, and reference bond lengths. Place the file wherever convenient. Note that the min.ff diorectory comes with a generic example of atomname2type.n2t.

3. **Generate the primitive topology**:
   ```bash
   gmx x2top \
     -f structure.pdb \
     -o structure.top \
     -ff minff \
     -param yes \
     -pbc yes \
     -n2t /absolute/path/to/atomname2type.n2t \
     -name MIN \
     -kb 441050 \
     -kt 500 \
     -ktH 110 \
     -aH 110 \
     -dH 0.09572
   ```
   Key flags:
   - `-ff minff` selects MINFF formatting and applies the MINFF defaults (bond distance output, MIN-only charge group, etc.).
   - `-n2t` points to your custom mapping file instead of the bundled force-field directory.
   - Adjust `-kb`, `-kt`, or `-ktH` if you need explicit force constants; otherwise the MINFF defaults (441050/500/110) are applied.
   - Optional refinements:
     - `-dH <nm>` forces hydrogen-involving bonds to use a chosen distance (and prints the corresponding force constant, defaulting to 441050 kJ mol⁻¹ nm⁻² if `-kb` is not set).
     - `-dM <nm>` overrides the printed bond length (); omit or set to `-1` to keep the MINFF defaults.
     - `-aH <deg>` overrides hydrogen-containing angles with a constant value (e.g. 110°) while leaving other angles geometry-derived.
     - `-pdbq yes` copies per-atom charges from the PDB B-factor column before the MINFF writer runs. Optional of course.
     - `-dM <nm>` overrides the printed bond length; omit or set to `-1` for the default MINFF formatting.
     - When neither flag is used, `[ bonds ]` falls back to the compact MINFF format (`index index 1 ; type-type`).


4. **Review the output**:
   - `structure.top` contains a MINFF-style `[ bonds ]` section (hydrogen-bearing bonds only, with bond distances), `[ angles ]` entries annotated with atom-type triplets, and a single charge group.
   - If you also emitted an RTP file (`-r out.rtp`), it will reflect the same atom typing and updated charges. Not sure about this..

5. **Proceed with GROMACS** – you can now combine the generated `.top` or `.itp` filewith other MINFF include files and continue with `gmx grompp`, `gmx mdrun`, etc., or edit it to extract the .itp part of the .top file to use it with other types of molecules in Gromacs.

## Troubleshooting Tips

- If `gmx x2top` cannot find atom types, double-check that every atom name listed in your coordinate file appears in the `.n2t` mapping (case-insensitive first character matching is used).
- When re-running after edits, clean or remove any previously generated topology files to avoid confusing downstream tools.
- Use `gmx help x2top` to confirm the updated option descriptions are visible; this confirms you are running the patched binary.

---
For deeper details on MINFF formatting, inspect `src/gromacs/gmxpreprocess/x2top.cpp` or the surrounding helper routines (`writeMinffTopology`, `writeMinffAnglesSection`, etc.).
