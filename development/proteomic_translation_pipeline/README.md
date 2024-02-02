# proteomic_translation_pipeline

Sets up project directory, project downloads, and converts nucleotide sequences to protein sequences.

## Table of Contents

- [Usage](#usage)
- [Workflow](#workflow)
- [Contributing](#contributing)
- [License](#license)

## Usage

To run `mixcr_pipeline.py`:

1. Activate `rl_bnab_maturation_pathways` conda environment.

```Bash
    # To activate conda environment:
    conda activate rl_bnab_maturation_pathways
```

2. Now you can run the python file.

```Bash
    # To run mixcr_pipeline.py
    python3 mixcr_pipeline.py <path_to_data_dir>
```

The path to the data directory is a required positional argument. This is the directory where the project files will be downloaded and processed.
> **Note:** The path to the data directory **must be an absolute path.**

This is necessary to ensure that files are written to the correct directories created relative to the data directory. 

Other arguments include:

- `--dataset`: this is name of the project.
- `--chains`: this describes which chains are being considered in this project. It is recommended to select all chains.
- `--fields`: this describes the fields to be stored in SQL database.
- `--skip_directory`: this skips directory setup & downloads. Assumes setup directory and only runs MiXCR pipeline.
- `--download-list`: this specifies the path to the txt file containing files to be downloaded.
- `--mode`: this specifies the output of MiXCR exportClones to be concise or verbose.

Please run the following for more details on expected input for each argument:

```Bash
    python3 mixcr_pipeline.py --help
```

A sample run:

```Bash
    python3 mixcr_pipeline.py /path/to/data \
                     --dataset RV217_40512 \
                     --chains IGK IGM IGG IGL \
                     --fields days \
                     --download-list \path\to\download-list.txt \

```

### Formatting `download-list.txt`

The format expected for the download list text file, which lists the web address to download data is as such:

```
<link_to_web_address>
  out=<rep_id>/<rep_id>_R1.fastq.gz
<link_to_web_address>
  out=<rep_id>/<rep_id>_R2.fastq.gz
```

The text file should have an even number of lines, where every two lines corresponds to the 1) link being accessed to download the data file and 2) path to the directory where the data file will be stored.

Notes:

- A separate process runs fie downlowds within the `raw` directory, hence the relative path shown above.
- This pipeline only supports **paired-end data**, hence for each repertoire (represented by a folder in `raw`), there should be two fastq corresponding to each of the two reads.

## Workflow

`mixcr_pipeline.py` sets up project directory structure and generates protein sequence for nucleotide datasets.

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
