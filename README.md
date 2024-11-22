
# MINFF: A New Forcefield for Molecular Simulations of Minerals

**MINFF** is a newly developed molecular dynamics (MD) forcefield designed for simulating Si, Al, Fe, Mg, Ca oxides and hydroxides, including hydrated clay minerals and zeolites. Developed to improve the accuracy of molecular simulations compared to existing forcefields, MINFF incorporates angle constraints, a large set of new atom types, and optimized Lennard-Jones parameters to achieve better agreement with experimental data. MINFF atomtype assignment is implemented in the **MATLAB Atom Toolbox** also available via the authors GitHub repository, which comes with HTML documentation and general examples for usage.

This forcefield family includes both a **general** and **tailor-made** versions optimized for over 30 mineral types, and has been tested for over 50 minerals. Each version is available in four configurations based on different angle force constants: **0, 250, 500, and 1500 kJ/mol/rad²**.

## Disclaimer

The MINFF forcefield parameters provided in this repository are still undergoing various tests and made available as-is and without any guarantee of their accuracy. It is hence the responsibility of any user to verify the accuracy and reliability of their simulations before relying on the results for any professional use. 

## Key Features
- **Generalized and Tailor-Made Forcefields**: The general version of MINFF is optimized across multiple minerals, while tailor-made versions are customized for specific minerals.
- **Multiple Configurations**: Available with four angle force constants to accommodate varying structural and vibrational properties:
  - **0 kJ/mol/rad²**: Similar to CLAYFF.
  - **250 and 500 kJ/mol/rad²**: Balanced accuracy for structural and vibrational properties.
  - **1500 kJ/mol/rad²**: Higher structural rigidity akin to INTERFACE FF (which for silicates uses 1422.56 kJ/mol/rad²).
- **Enhanced Compatibility**: Supports simulations of a wider range of minerals and includes atom types for Al, Mg, Fe(II/III), Ti, and Li.
- **Improved Accuracy**: Better reproduces bond distances, angles, and unit cell metrics compared to existing forcefields.

## Performance Highlights
- Median bond distance errors: ~1%, generally improving with increasing angle force constant
- Unit cell metric deviations: <0.5%, generally improving with increasing angle force constant
- Configurations with **250-500 kJ/mol/rad²** provide the best balance of structural and vibrational/elastic properties, but the MINFF version without angle constraints also perform well for certain minerals.

## Implementation
MINFF is implemented in the **MATLAB Atom Toolbox** and is available via its GitHub repository. It is compatible with Gromacs for running MD simulations and relies on advanced optimization routines for parameter fitting. For implementation in other simulation codes, send the author an email.

### Optimization Process
- Iterative MD simulations controlled by a MATLAB optimization algorithm, targeting individual bonds and angles (across PBC) and unit cell metrics.
- Charges obtained from **Chargemol/DDEC6** based on **CP2K** calculations using DZVP-MOLOPT-SR-GTH PP.
- Tailored for the **OPC3 water model**, ensuring compatibility with modern ion-pair potentials. Tests of (Na,K,Ca)-Montmorillonite hydration in close aggrement to CLAYFF+SPC/E behaviour. 

## Installation
MINFF is distributed through GitHub and the MATLAB Fileexchange and integrated into the MATLAB Atom Toolbox.

### Prerequisites
- MATLAB with the **Atom Toolbox** (v3.0 or later).

## Usage with the MATLAB Atom Toolbox

```matlab
% For general help, see inside each function or check out the Atom toolbox HTML documentation and general examples...

% Import the mineral structure, in a the .pdb, .gro or .xyz format (latter requires # Box_dim parameters in line 2)
% MÍNERAL is a indexed struct variable. Box_dim contains the simulation cell metrics.
[MINERAL,Box_dim]=import_atom(inputfile);

 % Assign the MINFF atomtype names
MINERAL=minff_atom(MINERAL,Box_dim)

% Adds a string for the forcefield version, currently not used
MINERAL=minff_atom(MINERAL,Box_dim,'minff')

% Write the new structure
write_atom_pdb(MINERAL,Box_dim,'minff_MINERAL.pdb')
write_atom_gro(MINERAL,Box_dim,'minff_MINERAL.gro') 
write_atom_xyz(MINERAL,Box_dim,'minff_MINERAL.xyz')

% Write a Gromacs topology file
write_atom_itp(MINERAL,Box_dim,'minff_MINERAL.itp',1.25,2.25) % * The first cutoff (1.25 Å) represents max bond distance to any H. The second cutoff (2.45 Å) represents the max bond distance between any non-H atomtypes, like Si-O.

```

1. Select the appropriate MINFF version (general or tailor-made) and angle force constant.
2. Prepare your input structure file with necessary atom types.
3. Run the MD simulation using Gromacs and the provided MINFF parameter files.

## References
A manuscript is in preparation.. as is the development of this repository..

## Contact
For questions or contributions, please contact:
- **Michael Holmboe**, Umeå University, Sweden  
  Email: [michael.holmboe@umu.se](mailto:michael.holmboe@umu.se)


