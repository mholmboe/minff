
# MINFF: A New Forcefield for Molecular Simulations of Minerals

**MINFF** is a newly developed molecular dynamics (MD) forcefield designed for simulating Si, Al, Fe, Mg, Ca, Ti, Li oxides and hydroxides, including hydrated clay minerals and zeolites. MINFF incorporates angle terms in addition to Lennard-Jones and Coloumbic terms to maintain accurate coordination environments and unit cell metrics, and introduces new atomtypes enabling the simulation of a wider range of minerals than current similar forcefields. MINFF atomtype assignment is implemented in the **MATLAB Atom Toolbox** also available via the authors GitHub repository, which comes with HTML documentation and general examples for usage.

This forcefield family includes both a **general** and **tailor-made** versions with Lennard-Jones parameters optimized for over 30 mineral types. Each general and tailor-made version is available in four sets based on different angle force constants: **0, 250, 500, and 1500 kJ/mol/rad²**. The new Lennard-Jones parameters for the general version can be found in the ffnonbonded.itp file for each respective angle force constant. Note that the listed charges for the oxygen atomtypes are just representative examples, and is computed per mineral by the Atom Toolbox using the charge smearing equation from Lammers et al 2017 (doi:10.1016/j.jcis.2016.11.084), during the atomtype assignment by the minff_atom function (see example below).

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

## References
A manuscript is in preparation.. as is the development of this repository..

## Contact
For questions or contributions, please contact:
- **Michael Holmboe**, Umeå University, Sweden  
  Email: [michael.holmboe@umu.se](mailto:michael.holmboe@umu.se)

### Optimization Process
- Iterative MD simulations controlled by a MATLAB optimization algorithm, targeting individual bonds and angles (across PBC) and unit cell metrics.
- Charges obtained from **Chargemol/DDEC6** based on **CP2K** calculations using DZVP-MOLOPT-SR-GTH PP.
- Tailored for the **OPC3 water model**, ensuring compatibility with modern ion-pair potentials. Tests of (Na,K,Ca)-Montmorillonite hydration in close aggrement to CLAYFF+SPC/E behaviour. 

## Installation
MINFF is distributed through GitHub and the [MATLAB Fileexchange](se.mathworks.com/matlabcentral/fileexchange/59622-atom) and integrated into the MATLAB Atom Toolbox.

### Prerequisites
- MATLAB with the **Atom Toolbox** (v3.0 or later).

## Usage

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


# Mineral List

A compact list of minerals with their corresponding numbers.

| Number | Mineral                           | Number | Mineral                           | Number | Mineral                             |
|--------|-----------------------------------|--------|-----------------------------------|--------|-------------------------------------|
| 1      | Kaolinite                         | 16     | Diaspore                          | 31     | Nacrite                            |
| 2      | Pyrophyllite                      | 17     | Periclase                         | 32     | Imogolite                          |
| 3      | Talc                              | 18     | Goethite                          | 33     | Anatase                           |
| 4      | Forsterite                        | 19     | Hematite                          | 34     | Rutile                            |
| 5      | Brucite                           | 20     | Lepidocrocite                     | 35     | 8_cis_Oct_Fe2_cis_GEO_OPT         |
| 6      | Corundum                          | 21     | Wüstite                           | 36     | 9_cis_Oct_Fe2_trans_GEO_OPT       |
| 7      | Quartz                            | 22     | Magnetite                         | 37     | 10_cis_Oct_Mg2cis_Fe3cis_GEO_OPT  |
| 8      | Gibbsite                          | 23     | CaF₂                              | 38     | 11_cis_Oct_Mg2cis_Fe3trans_GEO_OPT|
| 9      | Li₂O                              | 24     | CaO                               | 39     | 12_cis_Oct_Mg2trans_Fe3cis_GEO_OPT|
| 10     | Coesite                           | 25     | Portlandite                       | 40     | 13_cis_Oct_Mg2trans_Fe3trans_GEO_OPT|
| 11     | Cristobalite                      | 26     | Nontronite                        | 41     | 14_cis_Tet_Fe3_GEO_OPT            |
| 12     | Maghemite                         | 27     | Montmorillonite                   | 42     | 15_trans_Oct_Fe2_cis_GEO_OPT      |
| 13     | Quartz again                      | 28     | Dickite                           | 43     | 16_trans_Oct_Mg2cis_Fe3cis_GEO_OPT|
| 14     | Akdalaite                         | 29     | Hectorite-F                       | 44     | 17_trans_Tet_Fe3_GEO_OPT          |
| 15     | Boehmite                          | 30     | Hectorite-H                       | 45     | Muscovite                         |

**Notes:**

- Mineral 7 == Mineral 13.
- Mineral 27 = Montmorillonite adapted from Mineral 2, taken from Lee&Guggenheim (1981).
- Mineral 35-44 Montmorillonites adapted from Tsipursky&Drits (1984) smectite Models 1 and 2. 


## Mineral by category

Below is the classification of the listed minerals into suitable categories/classes, along with their respective numbers. Note that numbers **35-44** are different types of **Montmorillonites**, having different Fe(II)/(III)/Mg substitution sites.

---

## I. Silicates

### A. Tectosilicates (Framework Silicates)

1. **Quartz Group**
   - **Quartz** (**7**)
   - **Cristobalite** (**11**)
   - **Coesite** (**10**)

### B. Phyllosilicates (Sheet Silicates)

1. **Kaolinite Group (Kaolin Minerals)**
   - **Kaolinite** (**1**)
   - **Dickite** (**28**)
   - **Nacrite** (**31**)

2. **Smectite Group (Clay Minerals)**
   - **Montmorillonite** (**27**)
   - **Nontronite** (**26**)
   - **Hectorite**
     - **Hectorite-F** (**29**)
     - **Hectorite-H** (**30**)
   - **Montmorillonite Variants** (35-44)
     - **35**: 8_cis_Oct_Fe2_cis_GEO_OPT
     - **36**: 9_cis_Oct_Fe2_trans_GEO_OPT
     - **37**: 10_cis_Oct_Mg2cis_Fe3cis_GEO_OPT
     - **38**: 11_cis_Oct_Mg2cis_Fe3trans_GEO_OPT
     - **39**: 12_cis_Oct_Mg2trans_Fe3cis_GEO_OPT
     - **40**: 13_cis_Oct_Mg2trans_Fe3trans_GEO_OPT
     - **41**: 14_cis_Tet_Fe3_GEO_OPT
     - **42**: 15_trans_Oct_Fe2_cis_GEO_OPT
     - **43**: 16_trans_Oct_Mg2cis_Fe3cis_GEO_OPT
     - **44**: 17_trans_Tet_Fe3_GEO_OPT

3. **Mica Group**
   - **Muscovite** (**45**)

4. **Talc-Pyrophyllite Group**
   - **Talc** (**3**)
   - **Pyrophyllite** (**2**)

5. **Other Phyllosilicates**
   - **Imogolite** (**32**)

### C. Nesosilicates (Island Silicates)

- **Forsterite** (**4**)

---

## II. Oxides

### A. Simple Oxides

1. **Corundum Group**
   - **Corundum** (**6**)
   - **Akdalaite** (**14**)

2. **Hematite Group**
   - **Hematite** (**19**)
   - **Maghemite** (**12**)
   - **Magnetite** (**22**)
   - **Wüstite** (**21**)

3. **Rutile Group**
   - **Rutile** (**34**)
   - **Anatase** (**33**)

4. **Periclase Group**
   - **Periclase** (**17**)

### B. Hydroxide Oxides

- **Goethite** (**18**)
- **Lepidocrocite** (**20**)

---

## III. Hydroxides

- **Brucite** (**5**)
- **Gibbsite** (**8**)
- **Boehmite** (**15**)
- **Diaspore** (**16**)
- **Portlandite** (**25**)

---

## IV. Halides

- **Fluorite** (**23**)

---

## V. Other Compounds

- **Li₂O (Lithium Oxide)** (**9**)
- **CaO (Calcium Oxide)** (**24**)

---

### Notes:

- **Numbers 35-44 (Montmorillonite Variants):** These are different structural or compositional variants of Montmorillonite, a member of the Smectite group within the Phyllosilicates. The labels like "8_cis_Oct_Fe2_cis_GEO_OPT" refer to specific configurations or substitutions within the Montmorillonite structure, often used in computational models.

- **Kaolin Minerals (Kaolinite Group):** Kaolinite (**1**), Dickite (**28**), and Nacrite (**31**) are polymorphs of Al₂Si₂O₅(OH)₄, differing in stacking sequences of the silicate layers. Halloysite has not been modelled as of yet, but should work well with the Kaolinite parameters.

- **Hectorite (29, 30):** Hectorite-F and Hectorite-H represent different forms or treatments of Hectorite, a trioctahedral smectite clay mineral rich in magnesium and lithium.

- **Imogolite (32):** A hydrous aluminosilicate with a unique nanotubular structure, often found in volcanic ash soils.

- **Akdalaite (14):** Also known as "5Al₂O₃·H₂O", it is a hydrous aluminum oxide and can be classified with the Corundum group or as a hydroxide, depending on context.

---

## Summary by Category:

### Silicates

- **Phyllosilicates (Sheet Silicates):** 1, 2, 3, 26-32, 35-45
- **Tectosilicates (Framework Silicates):** 7, 10, 11, 13
- **Nesosilicates (Island Silicates):** 4

### Oxides and Hydroxides

- **Oxides:** 6, 12, 14, 17, 19, 21, 22, 33, 34
- **Hydroxides:** 5, 8, 15, 16, 18, 20, 25

### Halides

- **Halides:** 23

### Other Compounds

- **Oxides of Metals:** 9 (Li₂O), 24 (CaO)



