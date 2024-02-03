""" 
fasta_maker.py
This file generates a fasta file from all the covered sequences in the clones 
directory that match the specified chain requirement.
"""

import os
import csv
import argparse

""" -------------------- ARGPARSER -------------------- """

# Defining ArgumentParser class to parse command line arguments
parser = argparse.ArgumentParser(description="sequence selection pipeline")

# Arguments
parser.add_argument(
    "path_to_clones", type=str, help="path to data directory"
)  # /data/jgray21/iriver11/characterizing_bnabs/data

parser.add_argument(
    "-c",
    "--chains",
    dest="chains",
    nargs="+",
    type=str,
    default=["IGK"],
    help="generating fasta file for these chains",
)


""" -------------------- FORMAT UTILITY -------------------- """


def format_sequence(sequence: str) -> str:
    """
    Formats each sequence to fasta format requirement.
    All caps and no underscores.

    Parameters:
    sequence (string): sequence.

    Returns:
    sequence: formatted sequence
    """
    return sequence.split(" ", 1)[0].rstrip("_").upper()


def extract_sequences(path_to_repertoire: str, field: str) -> list:
    """
    Extracts sequences under the field column from a provided tsv.
    Ensures all sequence regions are covered.

    Parameters:
    path_to_repertoire (string): path to repertoire tsv file.
    field (string): name of the field to extract sequences from

    Returns:
    sequence (list): list of formatted sequences
    """
    sequences = list()
    try:
        if os.path.exists(path_to_repertoire):
            with open(path_to_repertoire, "r", newline="") as file:
                repertoire_reader = csv.DictReader(file, delimiter="\t")
                for row in repertoire_reader:
                    if field in row:

                        # verify that sequences are covered
                        sequence = format_sequence(row[field])
                        if hash(sequence) != hash("REGION_NOT_COVERED"):
                            sequences.append(sequence)

    except FileNotFoundError as e:
        print(f"File not found {path_to_repertoire}: {e}")

    return sequences


def write_fasta(sequences: list, repertoire: str, path_to_fasta: str) -> bool:
    """
    Writes sequences in the sequences array to a fasta file.

    Parameters:
    sequences (array): list of sequences extracted from {repertoire}.tsv.
    repertoire (string): name of the repertoire that sequences belongs to.
    path_to_fasta (string): path to fasta file.

    Returns:
    (bool): whether writing to fasta file was successful.
    """
    try:
        with open(path_to_fasta, "a") as file:
            for i, sequence in enumerate(sequences):
                file.write(f">{repertoire}_num{i}\n")
                file.write(f"{sequence}\n\n")

        return True

    except FileNotFoundError as e:
        print(f"Fasta file not found {path_to_fasta}: {e}")
        return False

    except IOError as e:
        print(f"Failed to write to fasta file {path_to_fasta}: {e}")
        return False


""" -------------------- MAIN -------------------- """


def main():

    args = parser.parse_args()

    chains = set(args.chains)
    path_to_clones = args.path_to_clones
    path_to_fasta = os.path.join(
        path_to_clones, f"chains-{'-'.join(chains)}_clones.fasta"
    )

    # Overwite fasta file
    with open(path_to_fasta, "w") as file:
        pass

    repertoires = os.listdir(args.path_to_clones)
    for repertoire in repertoires:
        repertoire_attributes = repertoire.split("-")
        for attribute in repertoire_attributes:
            if attribute.upper() in chains:
                path_to_repertoire = os.path.join(
                    path_to_clones, repertoire, f"{repertoire}_clones.tsv"
                )

                sequences = extract_sequences(
                    path_to_repertoire, "aaSeqImputedVDJRegion", path_to_clones
                )

                if not write_fasta(sequences, repertoire, path_to_fasta):
                    print("Writing to fasta failed. Please try again.")


if __name__ == "__main__":
    main()


# To run:
# python fasta_maker.py /Users/ivaneduardorivera/Projects/rl_bnab_maturation_pathways/test_suite/data/RV217_40512/clones/ -c IGK
