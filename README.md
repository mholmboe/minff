
# MINFF: A New Forcefield for Molecular Simulations of Minerals

**MINFF** is a newly developed molecular dynamics (MD) forcefield designed for simulating Si, Al, Fe, Mg, Ca, Ti, Li oxides and hydroxides, including hydrated clay minerals and zeolites. MINFF incorporates angle terms in addition to Lennard-Jones and Coloumbic terms to maintain accurate coordination environments and unit cell metrics, and introduces new atomtypes enabling the simulation of a wider range of minerals than current similar forcefields. MINFF atomtype assignment is implemented in the **MATLAB Atom Toolbox** also available via the authors GitHub repository, which comes with HTML documentation and general examples for usage.

This forcefield family includes both a **general** and **tailor-made** versions with Lennard-Jones parameters optimized for over 30 mineral types. Each general and tailor-made version is available in four sets based on different angle force constants: **0, 250, 500, and 1500 kJ/mol/rad²**.

## Disclaimer

The MINFF forcefield parameters provided in this repository are still undergoing various tests and made available as-is and without any guarantee of their accuracy. It is hence the responsibility of any user to verify the accuracy and reliability of their own simulations before relying on the results for any professional use. 

## Key Features
- **Generalized and Tailor-Made Forcefields**: The general version of MINFF was optimized across multiple minerals, while tailor-made versions was customized for specific minerals.
- **Multiple Configurations**: Available with four angle force constants to accommodate varying structural and vibrational properties:
  - **0 kJ/mol/rad²**: Meaning no angular constraints, similar to CLAYFF.
  - **250 and 500 kJ/mol/rad²**: Balanced accuracy for structural and vibrational properties.
  - **1500 kJ/mol/rad²**: Higher structural rigidity akin to INTERFACE FF (which for silicates uses 1422.56 kJ/mol/rad²).
- **Enhanced Compatibility**: Supports simulations of a wider range of minerals and includes atom types for Al, Fe(II/III), Mg, Ca, Ti, and Li.
- **Accuracy**: Parameterized for bond distances, angles, and unit cell metrics.

## Performance Highlights
The accuracy of MINFF is mineral-dependent, but overall:
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
MINFF is distributed through GitHub and the [MATLAB Fileexchange](se.mathworks.com/matlabcentral/fileexchange/59622-atom) and integrated into the MATLAB Atom Toolbox.

### Prerequisites
- MATLAB with the **Atom Toolbox** (v3.0 or later).

## Usage with the MATLAB Atom Toolbox

1. Select and download the appropriate MINFF version (general or tailor-made) and angle force constant.
2. Prepare your input structure file with necessary atom types.
3. Run the MD simulation using Gromacs and the provided MINFF parameter files (more info and examples to come).

```matlab
% For general help, see inside each function or check out the Atom toolbox HTML documentation and general examples...

% Import the mineral structure, in a the .pdb, .gro or .xyz format (latter requires # Box_dim parameters in line 2)
% MÍNERAL is a indexed struct variable. Box_dim contains the simulation cell metrics.
[MINERAL,Box_dim]=import_atom('inputfile.pdb'); 

 % Assign the MINFF atomtype names
MINERAL=minff_atom(MINERAL,Box_dim)

% Adds a string for the forcefield version, currently not used
MINERAL=minff_atom(MINERAL,Box_dim,'minff')

% Write a Gromacs topology file
write_atom_itp(MINERAL,Box_dim,'minff_MINERAL.itp',1.25,2.25) % * The first cutoff (1.25 Å) represents max bond distance to any H. The second cutoff (2.45 Å) represents the max bond distance between any non-H atomtypes, like Si-O.

% Write the new structure
write_atom_pdb(MINERAL,Box_dim,'minff_MINERAL.pdb')
write_atom_gro(MINERAL,Box_dim,'minff_MINERAL.gro') 
write_atom_xyz(MINERAL,Box_dim,'minff_MINERAL.xyz')

% or use the Atom toolbox to build an entire multicomponent system with counter-ions, water etc.

```

## References
A manuscript is in preparation.. as is the development of this repository..

## Contact
For questions or contributions, please contact:
- **Michael Holmboe**, Umeå University, Sweden  
  Email: [michael.holmboe@umu.se](mailto:michael.holmboe@umu.se)


