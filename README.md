
# MINFF: A New Forcefield for Molecular Simulations of Minerals

**MINFF** is a newly developed molecular dynamics (MD) forcefield designed for simulating Si, Al, Fe, Mg, Ca, Ti, Li oxides and hydroxides, including hydrated clay minerals and zeolites. MINFF incorporates angle terms in addition to Lennard-Jones and Coloumbic terms to maintain accurate coordination environments and unit cell metrics, and introduces new atomtypes enabling the simulation of a wider range of minerals than current similar forcefields. MINFF atomtype assignment is implemented in the [**MATLAB atom Toolbox**](https://github.com/mholmboe/atom) also available via this GitHub repository, which comes with HTML documentation and general examples for usage.

MINFF is a family of forcefields which includes both **general** version(s) and **tailor-made** versions for many specific minerals, using Lennard-Jones parameters optimized for over 30 mineral types. Furthermore, each general and tailor-made version is available in four different sets, with each set optimized for four different angle force constants: **0, 250, 500, and 1500 kJ/mol/rad²**. Currently MINFF has only been tested with Gromacs.

The new forcefield parameters for the general versions can be found in the Gromacs ffnonbonded.itp file for each respective angle force constant in the min.ff directory. The corresponding versions of the tailored parameters can be found in the files tminff_*_ffnonbonded.itp files, sorted either by angle force constant (see above) and/or mineral. Note tha the default version of the general and tailored sets of MINFF uses the Lennard-Jones parameters for the OPC3 water model for all oxygen atomtypes. There is however an alternative version (see commented out parameters) of the tailored versions of MINFF that uses independently optimized Lennard-Jones parameters for all oxygen atomtypes. Note also that the listed charges for the oxygen atomtypes in these files are just representative examples. The acutal oxygen charges should be computed specifically for each mineral/system by the [**atom Toolbox**](https://github.com/mholmboe/atom) using the charge smearing equation from Lammers et al 2017 (doi:10.1016/j.jcis.2016.11.084), during the atomtype assignment by the minff_atom function (see example below).

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
MINFF is implemented in the [**MATLAB atom Toolbox**](https://github.com/mholmboe/atom) and is available via its GitHub repository. It is compatible with Gromacs for running MD simulations and relies on advanced optimization routines for parameter fitting. For implementation in other simulation codes, send the author an email.

The mineral topology uses the minff_atom and the write_atom_itp functions of the [**atom Toolbox**](https://github.com/mholmboe/atom). 

The minff_atom functions uses a nearest-neighbour algorithm to determine the atomtypes/names, and sets the (Al, Si, Mg, Fe, Ca, Ti, Li, Fs) partial charges according to the MINFF forcefield, and calculates the corresponding oxygen neighbours charges by smearing/distributing the difference in formal and partial charge of the nearest non-oxygens over each oxygen site. This allows for generating custom oxygen sites resulting from for instance isomorphic substitution and or terminating edge-groups in clays (see for instance Lammers et al 2017, doi:10.1016/j.jcis.2016.11.084).

The write_atom_itp function prints a mineral topology file in the Gromacs .itp format, which will include all mineral O-H bonds (set to 0.9572Å and kb 441050 kJ/mol/nm²) and all M-O angles found in the input structure.


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
MINFF is distributed through GitHub and the [MATLAB Fileexchange](https://se.mathworks.com/matlabcentral/fileexchange/59622-atom) and integrated into the [**atom Toolbox**](github.com/mholmboe/atom).

### Prerequisites
- MATLAB with the [**atom Toolbox**](https://github.com/mholmboe/atom) (v3.0 or later).

## Usage

1. Select and download the appropriate MINFF version (general or tailor-made) and angle force constant.
2. Prepare your input structure file with necessary atom types.
3. Run the MD simulation using Gromacs and the provided MINFF parameter files (more info and examples to come).

```matlab
% For general help, see inside each function or check out the Atom toolbox HTML documentation and examples...

% Import the mineral structure, in a .pdb, .gro or .xyz format (latter requires # Box_dim parameters on line 2)
% MÍNERAL is a so-called indexed struct variable. The Box_dim variable contains the simulation cell metrics.
[MINERAL,Box_dim]=import_atom('inputfile.pdb');

% Optionally run the replicate_atom(), substitute_atom() or othe build functions to create/alter the mineral structure
% MINERAL=replicate_atom(MINERAL,Box_dim, [6 4 1]); % Will replicate a unit cell 6x4x1 times in x,y,z.
% MINERAL=substitute_atom(MINERAL,Box_dim,5,'Al','Mg',5.5); % Will substitute 5 (semi-)random Al sites for Mg, with a minimum distance of 5.5Å 

% Assign the MINFF atomtype names
MINERAL=minff_atom(MINERAL,Box_dim)

% Adds a string for the forcefield version, currently not used
MINERAL=minff_atom(MINERAL,Box_dim,'minff')

% Write a Gromacs topology file (currenlty only .itp files. .psf files coming soon..)
write_atom_itp(MINERAL,Box_dim,'minff_MINERAL.itp',1.25,2.25) % * The first cutoff (1.25 Å) represents max bond distance to any H. The second cutoff (2.45 Å) represents the max bond distance between any non-H atomtypes, like Si-O.

% Write the new structure
write_atom_pdb(MINERAL,Box_dim,'minff_MINERAL.pdb')
write_atom_gro(MINERAL,Box_dim,'minff_MINERAL.gro') 
write_atom_xyz(MINERAL,Box_dim,'minff_MINERAL.xyz')

% or use the Atom toolbox to build an entire multicomponent system with counter-ions, water etc. It is however to only use the minff_atom() function per mineral slab, and not on entire systems (which may contain waters, ions etc..)

```


# Mineral List

Below follows a description of the minerals (numbered after their order in the Systems folder) currently tested with the MINFF forcefield. Representative UC structures (without substitutions) can also be found under Systems/UC_conf/. Note also that the general MINFF forcefield parameters should also work well with other minerals sharing similar atomtypes, since optimization of the general MINFF versions was done synchronously for over 30 of the first listed minerals. For instance, the general MINFF parameters seems also to behave well with zeolites.

| Number | Mineral                           | Number | Mineral                           | Number | Mineral                            |
|--------|-----------------------------------|--------|-----------------------------------|--------|------------------------------------|
| 1      | Kaolinite                         | 16     | Diaspore                          | 31     | Nacrite                            |
| 2      | Pyrophyllite                      | 17     | Periclase                         | 32     | Imogolite                          |
| 3      | Talc                              | 18     | Goethite                          | 33     | Anatase                            |
| 4      | Forsterite                        | 19     | Hematite                          | 34     | Rutile                             |
| 5      | Brucite                           | 20     | Lepidocrocite                     | 35     | cis_Oct_Fe2_cis                    |
| 6      | Corundum                          | 21     | Wüstite                           | 36     | cis_Oct_Fe2_trans                  |
| 7      | Quartz                            | 22     | -                                 | 37     | cis_Oct_Mg2cis_Fe3cis              |
| 8      | Gibbsite                          | 23     | CaF₂                              | 38     | cis_Oct_Mg2cis_Fe3trans            |
| 9      | Li₂O                              | 24     | CaO                               | 39     | cis_Oct_Mg2trans_Fe3cis            |
| 10     | Coesite                           | 25     | Portlandite                       | 40     | cis_Oct_Mg2trans_Fe3trans          |
| 11     | Cristobalite                      | 26     | Nontronite                        | 41     | cis_Tet_Fe3                        |
| 12     | Maghemite                         | 27     | Montmorillonite                   | 42     | trans_Oct_Fe2_cis                  |
| 13     | -                                 | 28     | Dickite                           | 43     | trans_Oct_Mg2cis_Fe3cis            |
| 14     | Akdalaite                         | 29     | Hectorite-F                       | 44     | trans_Tet_Fe3_GEO_OPT              |
| 15     | Boehmite                          | 30     | Hectorite-H                       | 45     | Muscovite                          |

**Notes:**

- Mineral 13 and 22 missing and that's ok.
- Mineral 27 = Montmorillonite adapted from Mineral 2, taken from Lee&Guggenheim (1981).
- Mineral 35-44 Montmorillonites adapted from Tsipursky&Drits (1984) smectite Models 1 and 2. 


## Mineral by category

Below is the classification of the listed minerals into suitable categories/classes, along with their respective numbers. Note that numbers **35-44** are different types of **Montmorillonites**, having different Fe(II)/(III)/Mg substitution sites. Representative UC structures (without substitutions) can be found under Systems/UC_conf/.

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
     - **35**: cis_Oct_Fe2_cis
     - **36**: cis_Oct_Fe2_trans
     - **37**: cis_Oct_Mg2cis_Fe3cis
     - **38**: cis_Oct_Mg2cis_Fe3trans
     - **39**: cis_Oct_Mg2trans_Fe3cis
     - **40**: cis_Oct_Mg2trans_Fe3trans
     - **41**: cis_Tet_Fe3
     - **42**: trans_Oct_Fe2_cis
     - **43**: trans_Oct_Mg2cis_Fe3cis
     - **44**: trans_Tet_Fe3

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
- **Various Zeolites** (see Systems/UC_conf/zeolites)

---

### Notes:

- **Numbers 35-44 (Montmorillonite Variants):** These are different structural or compositional variants of Montmorillonite, a member of the Smectite group within the Phyllosilicates. The labels like "8_cis_Oct_Fe2_cis" refer to specific configurations or substitutions within the Montmorillonite structure, adapted from the Tsipursky&Drits (1984) models, and geometry optmized in CP2K. Number 27 is a hydrated Montmorillonite system with a charge of 2/3 q/UC in the octahedral layer adapted from Lee&Guggenheim (1981).

- **Kaolin Minerals (Kaolinite Group):** Kaolinite (**1**), Dickite (**28**), and Nacrite (**31**) are polymorphs of Al₂Si₂O₅(OH)₄, differing in stacking sequences of the silicate layers. Halloysite has not been modelled as of yet, but should work well with the Kaolinite parameters.

- **Hectorite (29, 30):** Hectorite-F and Hectorite-H represent different forms or treatments of Hectorite, a trioctahedral smectite clay mineral rich in magnesium and lithium.

- **Imogolite (32):** A hydrous aluminosilicate with a unique nanotubular structure, often found in volcanic ash soils.

- **Akdalaite (14):** Also known as "5Al₂O₃·H₂O", it is a hydrous aluminum oxide and can be classified with the Corundum group or as a hydroxide, depending on context.

---

# Mineral References

Original references for the used input structures. Note that most hydroxides and smectite structures were modified from the original structures by protonations and isomorphic substitutions.

| Order | Mineral                         | Reference                                                                                                                                                                                                                                                                          |
|-------|----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1     | Kaolinite                    | Bish, D.L. (1993). *Rietveld refinement of the kaolinite structure at 1.5 K*. Clays and Clay Minerals, 41, 738–744.                                                                                                                                            |
| 2     | Pyrophyllite                 | Lee, J.H., & Guggenheim, S. (1981). *Single crystal X-ray refinement of pyrophyllite-1Tc*. American Mineralogist, 66, 350–357.                                                                                                                                  |
| 3     | Talc                         | Rayner, J.H., & Brown, G. (1973). *The crystal structure of talc*. Clays and Clay Minerals, Proceedings of the Conference, 21, 103–114.                                                                                                                         |
| 4     | Forsterite                   | Fujino, K., Sasaki, S., Takeuchi, Y., & Sadanaga, R. (1981). *X-ray determination of electron distributions in forsterite, fayalite, and tephroite*. Acta Crystallographica, Section B, 37, 513–518.                                                            |
| 5     | Brucite                      | Catti, M., Ferraris, G., Hull, S., & Pavese, A. (1995). *Static compression and H disorder in brucite, Mg(OH)₂, to 11 GPa: a powder neutron diffraction study*.                                                                                                     |
| 6     | Corundum                     | d'Amour, H., Schiferl, D., Schulz, H., Denner, W., & Holzapfel, W.B. (1978). *High-pressure single-crystal structure determinations for ruby up to 90 kbar using an automatic diffractometer*. Journal of Applied Physics, 49, 4411–4416.                      |
| 7     | Quartz                       | Will, G., Bellotto, M., Parrish, W., & Hart, M. (1988). *Crystal structures of quartz and magnesium germanate by profile analysis of synchrotron-radiation high-resolution powder data*. Journal of Applied Crystallography, 21, 182–191.                      |
| 8     | Gibbsite                     | Saalfeld, H. (1961). *Strukturen des Hydrargillits und der Zwischenstufen beim Entwässern*. Neues Jahrbuch für Mineralogie, Abhandlungen, 95, 1–87.                                                                                                              |
| 9     | Li₂O                         | Wyckoff, R.W.G. (1963). *Second edition. Interscience Publishers, New York, New York: Anti-fluorite structure*. Crystal Structures, 1, 239–444.                                                                                                                 |
| 10    | Coesite                      | Levien, L., & Prewitt, C.T. (1981). *High-pressure crystal structure and compressibility of coesite: P = 1 atm isotropic refinement*. American Mineralogist, 66, 324–333.                                                                                       |
| 11    | Cristobalite                 | Downs, R.T., & Palmer, D.C. (1994). *The pressure behavior of alpha cristobalite: P = room pressure*. American Mineralogist, 79, 9–14.                                                                                                                         |
| 12    | Maghemite                    | Shmakov, A.N., Kryukova, G.N., Tsybulya, S.V., Chuvilin, A.L., & Solovyeva, L.P. (1995). Vacancy ordering in gamma-Fe₂O₃: Synchrotron x-ray powder diffraction and high-resolution electron microscopy studies. Journal of Applied Crystallography, 28, 141–145.  |
| 14    | Akdalaite                    | Yamaguchi, G., Okumiya, M., & Ono, S. (1969). *Refinement of the structure of tohdite 5Al₂O₃·H₂O*. Bulletin of the Chemical Society of Japan, 42, 2247–2249.                                                                                                     |
| 15    | Boehmite                     | Christensen, A.N., Lehmann, M.S., Convert, P., (1982). *Deuteration of crystalline hydroxides. Hydrogen bonds of gamma-AlOO(H,D) and gamma-FeOO(H,D)*. Acta Chemica Scandinavica A, 36, 303-308.                                                        |
| 16    | Diaspore                     | Ewing, F. (1935). *The crystal structure of diaspore*. Journal of Chemical Physics, 3, 203–207.                                                                                                                                                               |
| 17    | Periclase                    | Hazen, R.M. (1976). *Effects of temperature and pressure on the cell dimension and X-ray temperature factors of periclase*. American Mineralogist, 61, 266–271.                                                                                                 |
| 18    | Goethite                     | Nagai, T., Kagi, H., & Yamanaka, T. (2003). *Variation of hydrogen bonded O...O distances in goethite at high pressure*. American Mineralogist, 88, 1423–1427.                                                                                                  |
| 19    | Hematite                     | Maslen, E.N., Streltsov, V.A., Streltsova, N.R., & Ishizawa, N. (1994). *Synchrotron X-ray study of the electron density in α-Fe₂O₃*. Acta Crystallographica, Section B, 50, 435–441.                                                                           |
| 20    | Lepidocrocite                | Goldsztaub, M. (1935). *Étude de quelques dérivés de l'oxyde ferrique (FeO·OH, FeO₂Na, FeOCl): Détermination de leurs structures*. Bulletin de la Société Française de Minéralogie, 58, 6.                                                                     |
| 21    | Wüstite                      | Fjellvåg, H., Hauback, B.C., Vogt, T., & Stølen, S. (2002). *Monoclinic nearly stoichiometric wüstite at low temperatures*. American Mineralogist, 87, 347–349.                                                                                                 |
| 23    | CaF₂                         | Cheetham, A.K., Fender, B.E.F., & Cooper, M.J. (1971). *Defect structure of calcium fluoride containing excess anions: I. Bragg scattering*. Journal of Physics C: Solid State Physics, 4, 3107–3121.                                                         |
| 24    | CaO                          | Wyckoff, R.W.G. (1963). *Second edition. Interscience Publishers, New York, New York: Rocksalt structure*. Crystal Structures, 1, 85–237.                                                                                                                    |
| 25    | Portlandite                  | Pavese, A., Catti, M., Ferraris, G., & Hull, S. (1997). *P–V equation of state of portlandite, Ca(OH)₂, from powder neutron diffraction data*. Physics and Chemistry of Minerals, 24, 85–89.                                                                  |
| 26    | Nontronite                   | Dainyak, L.G., Zviagina, B.B., Rusakov, V.S., & Drits, V.A. (2006). *Interpretation of the nontronite-dehydroxylate Mössbauer spectrum using EFG calculations: Sample TV structure*. European Journal of Mineralogy, 18, 753–764.                             |
| 27    | Montmorillonite              | Lee, J.H., & Guggenheim, S. (1981). *Single crystal X-ray refinement of pyrophyllite-1Tc*. American Mineralogist, 66, 350–357.                                                                                                                                  |
| 28    | Dickite                      | Dera, P., Prewitt, C.T., Japel, S., Bish, D.L., & Johnston, C.T. (2003). *Pressure-controlled polytypism in hydrous layered materials*. American Mineralogist, 88, 1428–1435.                                                                                 |
| 29    | Hectorite-F                  | Seidl, W., & Breu, J. (2005). *Single crystal structure refinement of tetramethylammonium-hectorite*. Zeitschrift für Kristallographie, 220, 169–176.                                                                                                         |
| 30    | Hectorite-H                  | Seidl, W., & Breu, J. (2005). *Single crystal structure refinement of tetramethylammonium-hectorite*. Zeitschrift für Kristallographie, 220, 169–176.                                                                                                         |
| 31    | Nacrite                      | Zheng, H., & Bailey, S.W. (1994). *Refinement of the nacrite structure*. Clays and Clay Minerals, 42, 46–52.                                                                                                                                                 |
| 32    | Imogolite                    | Scalfi, L., Fraux, G., Boutin, A., & Coudert, F.-X. (2018). *Structure and dynamics of water confined in imogolite nanotubes*. Langmuir, 34, 6748–6756.                                                                                                       |
| 33    | Anatase                      | Playford, H.Y. (2020). *Variations in the local structure of nano-sized anatase TiO₂*. Journal of Solid State Chemistry, 288.                                                                                                                                 |
| 34    | Rutile                       | Sugiyama, K., & Takeuchi, Y. (1991). *The crystal structure of rutile as a function of temperature up to 1600°C*. Zeitschrift für Kristallographie, 194, 305–313.                                                                                             |
| 35    | cis_Oct_Fe2_cis              | Tsipurski, S.I., & Drits, V.A. (1984). *The distribution of octahedral cations in the 2:1 layers of dioctahedral smectites studied by oblique-texture electron diffraction*. Clay Minerals, 19, 177–193.                                                    |
| 36    | cis_Oct_Fe2_trans            | Tsipurski, S.I., & Drits, V.A. (1984). *The distribution of octahedral cations in the 2:1 layers of dioctahedral smectites studied by oblique-texture electron diffraction*. Clay Minerals, 19, 177–193.                                                    |
| 37    | cis_Oct_Mg2cis_Fe3cis        | Tsipurski, S.I., & Drits, V.A. (1984). *The distribution of octahedral cations in the 2:1 layers of dioctahedral smectites studied by oblique-texture electron diffraction*. Clay Minerals, 19, 177–193.                                                    |
| 38    | cis_Oct_Mg2cis_Fe3trans      | Tsipurski, S.I., & Drits, V.A. (1984). *The distribution of octahedral cations in the 2:1 layers of dioctahedral smectites studied by oblique-texture electron diffraction*. Clay Minerals, 19, 177–193.                                                 |
| 39    | cis_Oct_Mg2trans_Fe3cis      | Tsipurski, S.I., & Drits, V.A. (1984). *The distribution of octahedral cations in the 2:1 layers of dioctahedral smectites studied by oblique-texture electron diffraction*. Clay Minerals, 19, 177–193.                                                 |
| 40    | cis_Oct_Mg2trans_Fe3trans    | Tsipurski, S.I., & Drits, V.A. (1984). *The distribution of octahedral cations in the 2:1 layers of dioctahedral smectites studied by oblique-texture electron diffraction*. Clay Minerals, 19, 177–193.                                                 |
| 41    | cis_Tet_Fe3                  | Tsipurski, S.I., & Drits, V.A. (1984). *The distribution of octahedral cations in the 2:1 layers of dioctahedral smectites studied by oblique-texture electron diffraction*. Clay Minerals, 19, 177–193.                                                    |
| 42    | trans_Oct_Fe2_cis            | Tsipurski, S.I., & Drits, V.A. (1984). *The distribution of octahedral cations in the 2:1 layers of dioctahedral smectites studied by oblique-texture electron diffraction*. Clay Minerals, 19, 177–193.                                                    |
| 43    | trans_Oct_Mg2cis_Fe3cis      | Tsipurski, S.I., & Drits, V.A. (1984). *The distribution of octahedral cations in the 2:1 layers of dioctahedral smectites studied by oblique-texture electron diffraction*. Clay Minerals, 19, 177–193.                                                 |
| 44    | trans_Tet_Fe3                | Tsipurski, S.I., & Drits, V.A. (1984). *The distribution of octahedral cations in the 2:1 layers of dioctahedral smectites studied by oblique-texture electron diffraction*. Clay Minerals, 19, 177–193.                                                    |
| 45    | Muscovite                    | Rothbauer, R. (1971). *Untersuchung eines 2M₁-Muskovits mit Neutronenstrahlen*. Neues Jahrbuch für Mineralogie, Monatshefte, 1971, 143–154.                                                                                                                 |

---





