# PreStoi
## Predicting stoichiometry of protein complexes by integrating AlphaFold3 and templates.

This system was built and tested to predict the correct stoichiometry for targets released without stochiometry information (Phase 0) in the 16th worldwide Critical Assessment of Techniques for Protein Structure Prediction (CASP16) concluded in December 2024.

Using this system, MULTICOM4 achieved remarkable success, ranking 1st in protein complex structure prediction for such targets. 

## The workflow of the Stoichiometry Prediction system utilized by MULTICOM4 in CASP16
![Program workflow](images/workflow.png)

### This program handles both the template-based stoichiometry prediction and the AlphaFold3-based stoichiometry prediction part in the above diagram.




# Installation and Configuration

## System Requirements

- **Operating System**: Linux (Ubuntu 22.04 LTS recommended)  
- **Storage**: Up to **1 TB** (SSD recommended) for genetic databases  
- **GPU**: NVIDIA GPU with **Compute Capability 8.0+** (e.g., A100 80 GB, H100 80 GB)  
  - Supports inputs up to **5,120 tokens** on a single A100 or H100 (80 GB)  
- **RAM**: Minimum **64 GB** (especially for long targets) 

## Installation Time and Runtime Estimation

- **Installation Time**: Approximately **45 minutes** to download and set up databases (without SSD).  
- **Average Runtime**: Varies by target length, intended stoichiometries, and GPU memory. Inputs with up to **5,120 tokens** fit on an NVIDIA A100 or H100 (80 GB).
Example : Rutime of CASP16 target H0208
Sequence Lengths : Chain A : 328, Chain B : 318 <br />
Number of models generated per stoichiometry : 25 <br />
Device Configuration for running PreStoi and AlphaFold3:- CPU : AMD EPYC 7643 2.3 Ghz, RAM : 512 GB, GPU : One Nvidia A100 (80 GB) <br />
The average runtime of testing all 9 stoichiometry candidates (A1B1, A1B2, A1B3, A2B1, A2B2, A2B3, A3B1, A3B2, A3B3) is 266 minutes. 

## The PreStoi installation requires four steps:
### 1. Download PreStoi package
```
git clone https://github.com/jianlin-cheng/prestoi
cd prestoi
```

### 2. Install conda envoirment
You can create a virtual environment by yourself or install a fresh conda environment using the following commands:
```
wget "https://github.com/conda-forge/miniforge/releases/download/23.1.0-3/Mambaforge-$(uname)-$(uname -m).sh"
bash Mambaforge-$(uname)-$(uname -m).sh 
rm Mambaforge-$(uname)-$(uname -m).sh
source ~/.bashrc  
```
Then run the following commands to install the required python packages:
```
mamba install -y -c bioconda hmmer
pip install pandas biopython requests
```

### 3. Download databases and tools to make template-based predictions
```
python download_template_database_and_tools.py
```

### 4. AlphaFold3 installation. (Skip to step 5 if AlphaFold3 has already been installed)
### Begin with the installation of AlphaFold3 program using the following. 
https://github.com/google-deepmind/alphafold3/blob/main/docs/installation.md

Test whether AlphaFold3 program is working properly.
Once you have installed AlphaFold3, you can test your setup using e.g. the
following input JSON file named `fold_input.json`:

```json
{
  "name": "2PV7",
  "sequences": [
    {
      "protein": {
        "id": ["A", "B"],
        "sequence": "GMRESYANENQFGFKTINSDIHKIVIVGGYGKLGGLFARYLRASGYPISILDREDWAVAESILANADVVIVSVPINLTLETIERLKPYLTENMLLADLTSVKREPLAKMLEVHTGAVLGLHPMFGADIASMAKQVVVRCDGRFPERYEWLLEQIQIWGAKIYQTNATEHDHNMTYIQALRHFSTFANGLHLSKQPINLANLLALSSPIYRLELAMIGRLFAQDAELYADIIMDKSENLAVIETLKQTYDEALTFFENNDRQGFIDAFHKVRDWFGDYSEQFLKESRQLLQQANDLKQG"
      }
    }
  ],
  "modelSeeds": [1],
  "dialect": "alphafold3",
  "version": 1
}
```

You can then run AlphaFold 3 using the following command and check whether AlphaFold3 is running correctly:

```
docker run -it \
    --volume $HOME/af_input:/root/af_input \
    --volume $HOME/af_output:/root/af_output \
    --volume <MODEL_PARAMETERS_DIR>:/root/models \
    --volume <DATABASES_DIR>:/root/public_databases \
    --gpus all \
    alphafold3 \
    python run_alphafold.py \
    --json_path=/root/af_input/fold_input.json \
    --model_dir=/root/models \
    --output_dir=/root/af_output
```

### 5. Configure databases and tools for Stoichiometry Prediction

#### Run the configure.py to create a config.json file 
```
python configure.py --af3_program_path /path/to/alphafold3_program/ --af3_params_path /path/to/alphafold3_parameters/ --af3_db_path /path/to/alphafold3_databases/ --hhdb_prefix databases/pdb_sort90_2024/hhsuitedb3 --hhmake_binary tools/hhsuite-3.2.0/bin/hhmake --hhsearch_binary tools/hhsuite-3.2.0/bin/hhsearch --uniref90_path databases/uniref90_Pre-CASP16.fasta
```
This step will create a config.json file in the current working directory(prestoi) with the following information.
```json
{
  "af3_program_path": "/path/to/alphafold3_program/",
  "af3_params_path": "/path/to/alphafold3_parameters/",
  "af3_db_path": "/path/to/alphafold3_databases/",
  "uniref90_path": "/path/to/uniref90",
  "hhsearch_binary": "/path/to/hhsearch",
  "hhmake_binary": "/path/to/hhmake",
  "hhdb_prefix": "/path/to/hhdb",
}
```

Note: This step only requires running once. However, this can be run again if any of the above paths change. Make sure the paths are valid.

# Inference
## Run the template-based stoichiometry prediction
```
python template_based_prediction.py
```

The script requires 2 arguments:
  1. input_fasta : file path to the target fasta file
  2. output_path : desired output path for the results

This script will generate the possible number of copies for each subunit in the input FASTA file, generate stoichiometry candidates for AlphaFold3-based prediction, and provide template-based stoichiometry predictions when sufficient template evidence is available (e.g., a complex template that covers all subunits in the input FASTA)

Example output for H0208 (True stoichiometry: A1B1):
```
Subunit H0208_A: Possible Copies - [1, 2]
Subunit H0208_B: Possible Copies - [1, 2]
Stoichiometry candidates: ['A1B1', 'A1B2', 'A2B1', 'A2B2']
The chain number in 8d2z is less than the number of input subunits
[handle_single_template_stoich] Template=2yhe, cluster_stoich=A2, final_distribution=A1B1
Template-based stoichiometry prediction: A1B1
```

## Run the alphafold3-based stoichiometry prediction
```
python alphafold3_stoichiometry_prediction.py
```

The script requires 4 arguments:
  1. input_fasta : file path to the target fasta file
  2. stoichiometries : comma separated valid stoichiometries intended to be tested
  3. output_path : desired output path for the results
  4. num_models : number of models(in the multiple of 5) intended to be generated for each stoichiometry

 
This script will run all the required steps and print the results upon completion. Also /path/to/output_dir/ will contain a directory named after the input fasta file name which will contain:
  - input_jsons/ which contains the json files generated to be fed as inputs to AlphaFold3
  - AlphaFold3 outputs generated for different stoichiometries
  - stoichiometry_results.csv which contains a table of maximum and average ranking scores for each stoichiometry.


### Homomultimer Example
```
python alphafold3_stoichiometry_prediction.py --input_fasta /path/to/T0270o.fasta --stoichiometries A2,A3,A4,A5,A6 --output_path /path/to/output_dir  --num_models 25
```

Example output for T0270o (True stoichiometry: A3):
```
Stoichiometry results for :  T0270o

Stoichiometry, Maximum ranking score, Average ranking score, Number of models
A2,0.2917254023268046,0.22109988348999923,25
A3,0.7356659644178217,0.6597546325500054,25
A4,0.4619621540111602,0.4311053457765267,25
A5,0.5574578147810352,0.47328416184068417,25
A6,0.5455593923883584,0.4632293540739206,25

!!!!!!!!!!Final Selection!!!!!!!!!!

Stoichiometry with the highest Maximum ranking score: A3
Stoichiometry with the highest Average ranking score: A3
```

**Target T0270o**
| **Stoichiometries** | **Maximum Ranking Score** | **Average Ranking Score** | **Visualization**              |
| ------------------ | ------------------------- | -------------------------- | ------------------------------- |
| A2            | 0.2917254023268046        | 0.22109988348999923        | <img src="images/T0270o/A2.gif" alt="A2" width="320px" height="185px" /> |
| **A3**            | **0.7356659644178217**        | **0.6597546325500054**         | <img src="images/T0270o/A3.gif" alt="A3" width="320px" height="185px" /> |
| A4            | 0.4619621540111602        | 0.4311053457765267         | <img src="images/T0270o/A4.gif" alt="A4" width="320px" height="185px" /> |
| A5            | 0.5574578147810352        | 0.47328416184068417        | <img src="images/T0270o/A5.gif" alt="A5" width="320px" height="185px" /> |
| A6            | 0.5455593923883584        | 0.4632293540739206         | <img src="images/T0270o/A6.gif" alt="A6" width="320px" height="185px" /> |


### Heteromultimer Example
```
python alphafold3_stoichiometry_prediction.py --input_fasta /path/to/H0208.fasta --stoichiometries A1B1,A1B2,A1B3,A2B1,A2B2,A2B3,A3B1,A3B2,A3B3 --output_path /path/to/output_dir  --num_models 25
```

Example output for H0208 (True stoichiometry: A1B1):
```
Stoichiometry results for :  H0208

Stoichiometry, Maximum ranking score, Average ranking score, Number of models
A1B1,0.9579082725495932,0.9449554292400113,25
A1B2,0.7371544130131423,0.5392889019139051,25
A1B3,0.3972130584449553,0.35706427566899235,25
A2B1,0.8581746709490917,0.7907662683364439,25
A2B2,0.8726062852868774,0.6886386376967493,25
A2B3,0.5666602198361169,-15.505672491186171,25
A3B1,0.7930352000013527,0.7656765671860422,25
A3B2,0.4979020342021519,0.40007180256585756,25
A3B3,0.4140460397693776,0.37972803742981975,25

!!!!!!!!!!Final Selection!!!!!!!!!!

Stoichiometry with the highest Maximum ranking score: A1B1
Stoichiometry with the highest Average ranking score: A1B1
```
**Target H0208**
| **Stoichiometries** | **Maximum Ranking Score** | **Average Ranking Score** | **Visualization**                |
|------------------ |-------------------------- |--------------------------- |---------------------------------- |
| **A1B1**         | **0.9579082725495932**        | **0.9449554292400113**         | <img src="images/H0208/A1B1.gif" alt="A1B1" width="320px" height="185px" /> |
| A1B2         | 0.7371544130131423        | 0.5392889019139051         | <img src="images/H0208/A1B2.gif" alt="A1B2" width="320px" height="185px" /> |
| A1B3         | 0.3972130584449553        | 0.35706427566899235        | <img src="images/H0208/A1B3.gif" alt="A1B3" width="320px" height="185px" /> |
| A2B1         | 0.8581746709490917        | 0.7907662683364439         | <img src="images/H0208/A2B1.gif" alt="A2B1" width="320px" height="185px" /> |
| A2B2         | 0.8726062852868774        | 0.6886386376967493         | <img src="images/H0208/A2B2.gif" alt="A2B2" width="320px" height="185px" /> |
| A2B3         | 0.5666602198361169        | -15.505672491186171        | <img src="images/H0208/A2B3.gif" alt="A2B3" width="320px" height="185px" /> |
| A3B1         | 0.7930352000013527        | 0.7656765671860422         | <img src="images/H0208/A3B1.gif" alt="A3B1" width="320px" height="185px" /> |
| A3B2         | 0.4979020342021519        | 0.40007180256585756        | <img src="images/H0208/A3B2.gif" alt="A3B2" width="320px" height="185px" /> |
| A3B3         | 0.4140460397693776        | 0.37972803742981975        | <img src="images/H0208/A3B3.gif" alt="A3B3" width="320px" height="185px" /> |


## CASP16 Phase 0 Structural Models Availability

The AlphaFold3 structural models used to determine the stoichiometry for Phase 0 targets in CASP16 can be found at:
https://zenodo.org/records/14807606

## Reproduction Instruction

Most parts of the PreStoi method used in the blind CASP16 experiment can be automated and have been implemented in this GitHub repository. The automated results can be reproduced according to the following steps: (1) download the CASP16 Phase 0 protein complex dataset from this repository; (2) run PreStoi to propose stoichiometry candidates (template_based_prediction.py), generate AlphaFold3 structural models for them, and rank and select stoichiometries (alphafold3_stoichiometry_prediction.py);  (3) compare the stoichiometry prediction with the results in Table 1 in the manuscript describing PreStoi (https://www.biorxiv.org/content/10.1101/2025.01.12.632663v3). You may also compare the AlphaFold3 structural models and their ranking scores that you obtain with the ones generated in the CASP16 experiment that are available at https://zenodo.org/records/14807606. 

## Citing This Work

If you find this work useful, please cite: 

Liu, J., Neupane, P., & Cheng, J. (2025). Accurate Prediction of Protein Complex Stoichiometry by Integrating AlphaFold3 and Template Information. bioRxiv, 2025-01 (https://www.biorxiv.org/content/10.1101/2025.01.12.632663v3)

```bibtex
@article {Liu2025.01.12.632663,
	author = {Liu, Jian and Neupane, Pawan and Cheng, Jianlin},
	title = {Accurate Prediction of Protein Complex Stoichiometry by Integrating AlphaFold3 and Template Information},
	elocation-id = {2025.01.12.632663},
	year = {2025},
	doi = {10.1101/2025.01.12.632663},
	publisher = {Cold Spring Harbor Laboratory},
	URL = {https://www.biorxiv.org/content/10.1101/2025.01.12.632663v3},
	journal = {bioRxiv}
}
```
