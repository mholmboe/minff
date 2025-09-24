# MINFF-compatible `gmx x2top`

This is a modified version of `gromacs-2025.3/src/gromacs/gmxpreprocess/x2top.cpp` that streamlines MINFF force-field workflows, and which can handle bonds and angles across the PBC (-pbc yes). The key changes are:

- **MINFF-aware help text** – the command-line help and man page now describe the MINFF-specific output format, default force constants, and the `min`/`minff` force-field selectors.
- **Option descriptions** – the `-ff`, `-n2t`, `-name`, `-kb`, `-kt`, and `-ktH` option blurbs document the MINFF behaviour so the guidance appears both in `gmx help x2top` and generated manuals. Note that with -n2t a custom .n2t file can be used.
- **Default handling** – internally, the code already applied MINFF defaults (bond distance printing, charge-group collapse, etc.); the documentation now matches that runtime behaviour.

No functional regressions were introduced—the program still honours charges read from a PDB/PDBQ file when you pass `-pdbq yes`, even when MINFF formatting is selected.

## Installing the patched x2top tool in GROMACS

1. **Download and Copy/Overwrite** 
   - Download Gromacs as you are use to..
   - Copy the modified version of x2top.cpp to gromacs-2025.3/src/gromacs/gmxpreprocess/x2top.cpp, ie overwrite the original version of x2top.cpp. Note that it likely works on other versions as well

2. **Build and Install**:
   - Do a normal installation of Gromacs
  
3. **Test the installation**:
   - Run gmx x2top -h. Does the instructions mention minff? 
     

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
     -kb 125 \
     -kt 500 \
     -ktH 125 
   ```
   Key flags:
   - `-ff minff` selects MINFF formatting and applies the MINFF defaults (bond distance output, MIN-only charge group, etc.).
   - `-n2t` points to your custom mapping file instead of the bundled force-field directory.
   - `-pdbq yes` copies per-atom charges from the PDB B-factor column before the MINFF writer runs.
   - Adjust `-kb`, `-kt`, or `-ktH` if you need explicit force constants; otherwise the MINFF defaults (441050/500/125) are applied.

4. **Review the output**:
   - `structure.top` contains a MINFF-style `[ bonds ]` section (hydrogen-bearing bonds only, with bond distances), `[ angles ]` entries annotated with atom-type triplets, and a single charge group.
   - If you also emitted an RTP file (`-r out.rtp`), it will reflect the same atom typing and updated charges.

5. **Proceed with GROMACS** – you can now combine the generated `.top` with other MINFF include files and continue with `gmx grompp`, `gmx mdrun`, etc., or edit it to extract the .itp part of the .top file to use it with other types of molecules in Gromacs.

## Troubleshooting Tips

- If `gmx x2top` cannot find atom types, double-check that every atom name listed in your coordinate file appears in the `.n2t` mapping (case-insensitive first character matching is used).
- When re-running after edits, clean or remove any previously generated topology files to avoid confusing downstream tools.
- Use `gmx help x2top` to confirm the updated option descriptions are visible; this confirms you are running the patched binary.

---
For deeper details on MINFF formatting, inspect `src/gromacs/gmxpreprocess/x2top.cpp` or the surrounding helper routines (`writeMinffTopology`, `writeMinffAnglesSection`, etc.).
