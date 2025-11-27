# FF Parameters Export

This folder contains JSON exports of MINFF force field parameters generated from GROMACS `ffnonbonded_*.itp` and `ffbonded.itp` files, which contain the atomtype definitions and non-bonded and bonded parameters for (G/T)MINFF, as well as many ion-pair parameters and water models.

`gmx2json.py` converts `ffnonbonded_*.itp` and `ffbonded.itp` into a JSON layout that preserves:
- `common_atomtypes`: unconditional entries (e.g., water) present outside any `#ifdef`.
- `nonbonded_blocks`: atomtypes per `#ifdef` block.
- `bondtypes` and `angletypes`: taken from the bonded file.
- `metadata`: file paths, selected blocks, available blocks, and units.

Quick usage
- List blocks:\
  `python gmx2json.py -nb ../min.ff/ffnonbonded_gminff.itp --list-blocks`
- Export selected blocks:\
  `python gmx2json.py -nb ../min.ff/ffnonbonded_gminff.itp -b ../min.ff/ffbonded.itp -blocks GMINFF_k500 OPC3_HFE_LM -o GMINFF/gminff_opc3_hfe_lm_k500.json`
- You can also rely on `--variant`/`--input_dir` if you prefer:\
  `python gmx2json.py --variant gminff --input_dir ../min.ff --list-blocks`

Flags of interest
- `-nb, --nonbonded-file` path to `ffnonbonded*.itp`.
- `-b, --bonded-file` path to `ffbonded*.itp` (falls back to `ffbonded.itp` if omitted and available).
- `-blocks, --blocks` one or more `#ifdef` block names to export.
- `--list-blocks` show available blocks and exit.
- `-o, --output` output JSON path (defaults to `minff_<variant>.json` when `--variant` is used).
