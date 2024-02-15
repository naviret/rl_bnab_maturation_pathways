# Characterizing Broadly Neutralizing Antibodies Using Reinforcement Learning

This repository develops a toolkit aimed at characterizing the maturation pathway of broadly neutralizing antibodies using artificial intelligence and deep learning aproaches.

## Motivation

Antibody-mediated immunity plays a crucial role in the adaptive immune response by providing neutralization activity against a number of pathogens. However, many human pathogens, such as Human Immunodeficiency Virus (HIV), Influenza, and Coronavirus, evade neutralization by rapidly mutating their epitopes, and concealing other functionally-important and highly-conserved epitopes. Broadly neutralizing antibodies (bnAbs) have shown promise in treating rapidly mutating pathogens because of their ability to target conserved regions, and an understanding of their maturation pathways would provide insight into optimal vaccination protocols. In this work, we propose a soft actor-critic reinforcement learning architecture to characterize key features in the maturation from germline to bnAb for antibodies targeting the MPER epitope of the HIV-1 protein.

## Table of Contents

- [Installation](#installation)
- [Modules](#scripts)
- [Under Development](#underdevelopment)
- [Contributing](#contributing)
- [License](#license)

## Installation

To use the scripts developed in this repository, you must clone this repository and create a conda environment to hold necessary packges.

1.  Clone this repo onto local directory:

```Bash
    # To clone repo onto local directory:
    git clone https://github.com/naviret/rl_bnab_maturation_pathways.git
```

2. Create a conda environment called `rl_bnab_maturation_pathways` using `requirements.txt` file in the repo's root directory. Make sure the `requirements.txt` is in your current directory.

```Bash
    # To create conda environment:
    conda create --name rl_bnab_maturation_pathways --file requirements.txt
```

3. Activate `rl_bnab_maturation_pathways` conda environment.

```Bash
    # To activate conda environment:
    conda activate rl_bnab_maturation_pathways
```

After activation your terminal should display the activated conda environment:

```Bash

    (rl_bnab_maturation_pathways) user@machine rl_bnab_maturation_pathways $

```

## Modules

This repository has the following modules available:

<pre>
.
└── data/
    ├── &ltproject_title&gt/
    │   ├── &ltproject_title>.db
    │   ├── raw/
    │   │   ├── download-list.txt
    │   │   ├── &ltrep_id&gt/
    │   │   │   ├── &ltrep_id&gt_R1.fastq.gz
    │   │   │   └── &ltrep_id&gt_R2.fastq.gz
    │   │   └── ... 
    │   └── clones/
    │       ├── &ltrep_id&gt/
    │       │   └── &ltrep_id&gt_clones.tsv
    │       └── ...
    └── ...
</pre>

### Step 1: Download Raw Files

`mixcr_pipeline.py` sets up the `raw` directory by copying the download text file onto `download-list.txt`. Then, it will use `aria2c` download utility to optimize and fail-proof file downloads. `mixcr_pipeline.py` will fork a subprocess to attempt download up to 10 times, and quit upon more than 10 failures.

### Step 2: Create Clones Directory

`mixcr_pipeline.py` sets up the `clones` directory by creating all `<rep_id>` the folders in `raw`. These folders remain empty until MiXCR commands.

### Step 3. Run Alignments and Assemble

`mixcr_pipeline.py` runs alignments of the nucleotide sequences with known CD3 and VDJ gene regions in human species. It will then assemble contiguous clonotypes using these alignments. Alignment and assemble are ran in a single step using `MiXCR`, a software tool designed for the analysis of T-cell receptor (TCR) and B-cell receptor (BCR) repertoires. `mixcr_pipeline.py` will run alignment and assemble in batches of 6 repertoires, where each repertoire is started in its own process, thus increasing execution speed by executing them in parallel. Alignments are stored in each repertoire's respective `raw` directory.

> Execution time expectation is 10 to 15 minutes per batch.

### Step 4. Export Clones

Similar to step 3, `mixcr_pipeline.py` uses parallelized processes to extract assembled contiguous antibody sequences. These are stored in each repertoires respective directory within the `clones` directory, signified by their `<rep_id>`.

## Contributing

Contributions are welcome! Please follow these guidelines for contributions:

- Fork the repository
- Create a new branch: `git checkout -b feature-name`
- Make your changes and commit them: `git commit -m 'Description of changes'`
- Push to the branch: `git push origin feature-name`
- Submit a pull request

## License

This project is licensed under the [MIT License](LICENSE).
