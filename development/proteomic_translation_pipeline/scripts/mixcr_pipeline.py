""" 
mixcr_pipeline.py
This file downloads all the data from specified nucleotide data set, translates all the nucleotide
data to proteomic data using aligments.
"""

import os
import sys
import time
import shutil
import sqlite3
import argparse
import subprocess
from math import ceil


""" -------------------- ARGPARSER -------------------- """

# Defining ArgumentParser class to parse command line arguments
parser = argparse.ArgumentParser(
    description="directory \
                                 set up and MiXCR pipeline"
)

# Arguments
parser.add_argument("data_path", type=str, help="path to data directory")

parser.add_argument(
    "--dataset",
    dest="dataset",
    type=str,
    default="RV217_40512",
    help="name of data set",
)

parser.add_argument(
    "-c",
    "--chains",
    dest="chains",
    nargs="+",
    type=str,
    default=["IGK", "IGM", "IGG", "IGL"],
    help="chains expected in the data set",
)

parser.add_argument(
    "--fields",
    dest="fields",
    nargs="+",
    type=str,
    default=["day"],
    help="additional database fields \
        + DEFAULT repertoire path",
)

parser.add_argument(
    "--skip-directory",
    dest="skip_directory",
    action="store_true",
    help="skip directory set up & \
        downloads. only MiXCR pipeline",
)

parser.add_argument(
    "-d",
    "--download-list",
    dest="download_list",
    type=str,
    default="download-list.txt",
    help="txt of .fastq files to download",
)

parser.add_argument(
    "-m",
    "--mode",
    dest="mixcr_mode",
    type=str,
    default="CONCISE",
    help="exportClones mode is \
        either CONCISE or VERBOSE",
)

args = parser.parse_args()  # Object that stores parsed arguments

# Accesses parsed arguments from ArgumentParser
data_dir = args.data_path
data_set = args.dataset
chains = set(args.chains)
fields = ["repertoire_address", "chain"] + args.fields
skip_directory = args.skip_directory
ori_download_list = args.download_list
mixcr_mode = args.mixcr_mode  ##### [FUTURE DEV] #####


""" -------------------- DOWNLOAD UTILITY -------------------- """


def download_with_aria(d_list, raw_data_dir):
    """
    Downloads linked files using aria2c by
    starting a separate process.

    Parameters:
    d_list (string): string to txt with linked files.

    Returns:
    tuple: A tuple containing the following:
        - returncode (int): process success
        - stdout (string): process standard output
        - stder (string): process standard error
    int: The sum of the two numbers.
    """

    command = [
        "aria2c",
        "--console-log-level=error",
        "--download-result=hide",
        "-c",
        "-s",
        "16",
        "-x",
        "16",
        "-k",
        "1M",
        "-j",
        "8",
        "-i",
        d_list,
    ]

    # Spawns aria2c download process
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=raw_data_dir,
        text=True,
    )
    process.wait()

    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


""" -------------------- MIXCR FUNCTION WRAPPERS -------------------- """


def MiXCR_analyze(repertoires, raw_data_dir, batch_size=6):
    """
    Execute MiXCR analyze with sequence
    alignments and assemble steps in
    parallelized process.

    Parameters:
    repertoires (list): list of repertoires.
    batch_size (int, optional): number of MiXCR analyze
    to execute in one batch.

    Returns:
    None
    """

    for i in range(0, len(repertoires), batch_size):
        rep_batch = repertoires[i : i + batch_size]

        print(
            f"Running batch {i//batch_size + 1} of {ceil(len(repertoires)/batch_size)}."
        )

        processes = list()

        for rep in rep_batch:
            rep_dir = os.path.join(raw_data_dir, rep)

            MiXCR = [
                "mixcr",
                "analyze",
                "generic-amplicon",
                "--species",
                "hs",
                "--rna",
                "--floating-left-alignment-boundary",
                "--floating-right-alignment-boundary",
                "C",
                "--drop-non-CDR3-alignments",
                "--assemble-contigs-by",
                " VDJRegion",
                "--remove-step",
                "exportClones",
                f"{rep}_R1.fastq.gz",
                f"{rep}_R2.fastq.gz",
                f"{rep}_clones",
            ]

            process = subprocess.Popen(
                MiXCR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=rep_dir,
                text=True,
            )

            processes.append(process)

        # Wait on all processes
        for j, p in enumerate(processes):
            p.wait()

            # Display returncode at failure
            if p.returncode != 0:
                stdout, stderr = p.communicate()
                print(
                    f"Execution of repertoire {i + j + 1}, {rep_batch[j]} failed with exit code {p.returncode}."
                )

                print(f"Out: {stdout}")
                print(f"Error: {stderr}")


# def MiXCR_export(repertoires, raw_data_dir, clones_data_dir, batch_size=12):
#     """
#     Execute MiXCR exportClones in
#     parallelized processes.

#     Parameters:
#     repertoires (list): list of repertoires.
#     batch_size (int, optional): number of MiXCR analyze
#     to execute in one batch.

#     Returns:
#     None
#     """

#     for i in range(0, len(repertoires), batch_size):
#         rep_batch = repertoires[i : i + batch_size]

#         print(
#             f"Running batch {i//batch_size + 1} of {ceil(len(repertoires)/batch_size)}."
#         )

#         processes = list()

#         for rep in rep_batch:
#             # Extract chain
#             chain = None
#             rep_fields = rep.split("-")
#             for r in rep_fields:
#                 if r.upper() in chains:
#                     chain = r.upper()

#             rep_dir = os.path.join(raw_data_dir, rep)
#             rep_clones_dir = os.path.join(
#                 clones_data_dir, rep, f"{rep}_clones.tsv"
#             )

#             MiXCR = [
#                 "mixcr",
#                 "exportClones",
#                 "--export-productive-clones-only",
#                 "--impute-germline-on-export",
#                 "--drop-default-fields",
#                 "-cloneId",
#                 "-readCount",
#                 "-aaFeatureImputed VDJRegion",
#                 "-nFeatureImputed VDJRegion",
#                 f"--chains {chain}" if chain is not None else None,
#                 f"{rep}_clones.clns",
#                 f"{rep_clones_dir}",
#             ]

#             # Remove None from list
#             MiXCR = [arg for arg in MiXCR if arg is not None]

#             process = subprocess.Popen(
#                 MiXCR,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 cwd=rep_dir,
#                 text=True,
#             )
#             processes.append(process)

#         # Wait on all processes
#         for j, p in enumerate(processes):
#             p.wait()

#             # Display returncode at failure
#             if p.returncode != 0:
#                 stdout, stderr = p.communicate()
#                 print(
#                     f"Execution of repertoire {i + j + 1}, {rep_batch[j]} failed with exit code {p.returncode}."
#                 )
#                 print(f"Out: \n{stdout}.")
#                 print(f"Error: \n{stderr}.")


def MiXCR_export(
    repertoires, data_dir, raw_data_dir, clones_data_dir, batch_size=12
):
    """
    Execute MiXCR exportClones in
    parallelized processes.

    Parameters:
    repertoires (list): list of repertoires.
    batch_size (int, optional): number of MiXCR analyze
    to execute in one batch.

    Returns:
    None
    """

    for i in range(0, len(repertoires), batch_size):
        rep_batch = repertoires[i : i + batch_size]

        print(
            f"Running batch {i//batch_size + 1} of {ceil(len(repertoires)/batch_size)}."
        )

        processes = list()

        for rep in rep_batch:
            # Extract chain
            chain = None
            rep_fields = rep.split("-")
            for r in rep_fields:
                if r.upper() in chains:
                    chain = r.upper()

            rep_raw_path = os.path.join(raw_data_dir, rep, f"{rep}_clones.clns")
            rep_clones_path = os.path.join(
                clones_data_dir, rep, f"{rep}_clones.tsv"
            )

            MiXCR = [
                "mixcr",
                "exportClones",
                "--export-productive-clones-only",
                "--impute-germline-on-export",
                "--drop-default-fields",
                "-cloneId",
                "-readCount",
                "-aaFeatureImputed VDJRegion",
                "-nFeatureImputed VDJRegion",
                f"--chains {chain}" if chain is not None else None,
                f"{rep_raw_path}",
                f"{rep_clones_path}",
            ]

            # Remove None from list
            MiXCR = [arg for arg in MiXCR if arg is not None]

            process = subprocess.Popen(
                MiXCR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=data_dir,
                text=True,
            )
            processes.append(process)

        # Wait on all processes
        for j, p in enumerate(processes):
            p.wait()

            # Display returncode at failure
            if p.returncode != 0:
                stdout, stderr = p.communicate()
                print(
                    f"Execution of repertoire {i + j + 1}, {rep_batch[j]} failed with exit code {p.returncode}."
                )
                print(f"Out: {stdout}")
                print(f"Error: {stderr}")


""" -------------------- MAIN -------------------- """


def main():
    """
    Main function.

    Parameters:
    None

    Returns:
    None
    """

    """ 
    Extract path to directories. 
    """
    data_set_dir = os.path.join(data_dir, data_set)  # dataset dir
    raw_data_dir = os.path.join(data_set_dir, "raw")  # raw dir
    clones_data_dir = os.path.join(data_set_dir, "clones")  # clones dir
    sql_db = os.path.join(data_set_dir, f"{data_set}.db")  # sql db

    # relative dirs
    rel_raw_data_dir = os.path.join(data_set, "raw")
    rel_clones_data_dir = os.path.join(data_set, "clones")

    """
    Create directory 
    structure and download files. 
    """
    if not skip_directory:
        # Create directories
        try:
            os.mkdir(data_set_dir)
            os.mkdir(raw_data_dir)
            os.mkdir(clones_data_dir)
        except FileExistsError:
            print(
                "Directory already exists. Re-run with --skip-directory.",
                file=sys.stderr,
            )

        # Copy download list to raw data dir.
        download_list = "download-list.txt"
        raw_dir_download_list = os.path.join(raw_data_dir, download_list)
        shutil.copy(ori_download_list, raw_dir_download_list)

        # Download linked files.
        max_tries = 10  # attempt 10 times.
        for i in range(max_tries):
            sys.stdout.write("Downloading...\n")
            exit_code, stdout, stderror = download_with_aria(
                download_list, raw_data_dir
            )
            if exit_code == 0:
                sys.stdout.write("Download succesful.\n")
                break

            else:
                sys.stdout.write(
                    f"\nDownload attempt {i + 1} failed with exit code: {exit_code}. "
                )
                sys.stdout.write(f"{stdout}")
                time.sleep(5)

        # Failure.
        if exit_code != 0:
            raise Exception("Download failed.")

        # Set up clones directory.
        repertoires = list()
        for rep in os.listdir(raw_data_dir):
            if os.path.isdir(os.path.join(raw_data_dir, rep)):
                rep_dir = os.path.join(clones_data_dir, rep)
                os.mkdir(rep_dir)

    """
    Create sqlite3 databse
    """
    # Extract sql db fields.
    fields_query = ", ".join([f"{f} TEXT NOT NULL" for f in fields])

    # Open and create a sqlite3 database.
    with sqlite3.connect(sql_db) as connect:
        cursor = connect.cursor()
        cursor.execute(
            f"""
            CREATE TABLE repertoire (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {fields_query} ) 
        """
        )

        # Applying data creation changes.
        connect.commit()

    """
    Insert meta info into
    sqlite3 database for each
    repertoire
    """
    # Extract repertoire names.
    repertoires = [
        rep
        for rep in os.listdir(raw_data_dir)
        if os.path.isdir(os.path.join(raw_data_dir, rep))
    ]

    # Extract field entries.
    insert = list()
    for i, rep in enumerate(repertoires):
        # Repertoire names
        rep_fields = rep.split("-")
        rep_dict = {"repertoire_address": rep}

        # Extract only desired fields.
        for r in rep_fields:
            if r.upper() in chains:
                rep_dict["chain"] = r.upper()

            for f in fields:
                if f in r:
                    rep_dict[f] = r.lower()

        # Checks for valid insert row, skips if invalid
        try:
            rep_insert = [rep_dict[f] for f in fields]
        except KeyError:
            continue

        insert.append(tuple(rep_insert))

    # Insert into database.
    insert_query = ", ".join(fields)

    with sqlite3.connect(sql_db) as connect:
        # Begin a transaction.
        connect.execute("BEGIN")

        # Create cursor to write to database.
        cursor = connect.cursor()

        # Execute query.
        cursor.executemany(
            f""" 
                INSERT INTO repertoire ({insert_query})
                    VALUES ({", ".join(["?"] * len(fields))})
            """,
            insert,
        )

        # Save changes.
        connect.commit()

    """
    Execute MiXCR Pipeline
    """

    # Run alignment + assemble.
    print("Run MiXCR alignment + assemble.")
    MiXCR_analyze(repertoires=repertoires, raw_data_dir=raw_data_dir)

    # Run export clones.
    print("Run MiXCR export clones.")
    # MiXCR_export(
    #     repertoires=repertoires,
    #     raw_data_dir=raw_data_dir,
    #     clones_data_dir=clones_data_dir,
    # )
    MiXCR_export(
        repertoires=repertoires,
        data_dir=data_dir,
        raw_data_dir=rel_raw_data_dir,
        clones_data_dir=rel_clones_data_dir,
    )


if __name__ == "__main__":
    main()


### NOTES:
### data dir: # /data/jgray21/iriver11/characterizing_bnabs/data
### To run locally: python ../scripts/mixcr_pipeline.py data
### its okay if i provide a
### provide absolute data path
### relative path from where mixcr_pipeline is
### relative path to mixcr_pipeline.py and run at data's parent
### WHY? because everything is built from where parent is run and relative to data dir


# def MiXCR_export(
#     repertoires, data_dir, raw_data_dir, clones_data_dir, batch_size=12
# ):
#     """
#     Execute MiXCR exportClones in
#     parallelized processes.

#     Parameters:
#     repertoires (list): list of repertoires.
#     batch_size (int, optional): number of MiXCR analyze
#     to execute in one batch.

#     Returns:
#     None
#     """

#     for i in range(0, len(repertoires), batch_size):
#         rep_batch = repertoires[i : i + batch_size]

#         print(
#             f"Running batch {i//batch_size + 1} of {ceil(len(repertoires)/batch_size)}."
#         )

#         processes = list()

#         for rep in rep_batch:
#             # Extract chain
#             chain = None
#             rep_fields = rep.split("-")
#             for r in rep_fields:
#                 if r.upper() in chains:
#                     chain = r.upper()

#             rep_raw_path = f"{os.path.join(raw_data_dir, rep)}_clones.clns"
#             rep_clones_path = os.path.join(
#                 clones_data_dir, rep, f"{rep}_clones.tsv"
#             )

#             MiXCR = [
#                 "mixcr",
#                 "exportClones",
#                 "--export-productive-clones-only",
#                 "--impute-germline-on-export",
#                 "--drop-default-fields",
#                 "-cloneId",
#                 "-readCount",
#                 "-aaFeatureImputed VDJRegion",
#                 "-nFeatureImputed VDJRegion",
#                 f"--chains {chain}" if chain is not None else None,
#                 f"{rep_raw_path}",
#                 f"{rep_clones_path}",
#             ]

#             # Remove None from list
#             MiXCR = [arg for arg in MiXCR if arg is not None]

#             process = subprocess.Popen(
#                 MiXCR,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 cwd=data_dir,
#                 text=True,
#             )
#             processes.append(process)

#         # Wait on all processes
#         for j, p in enumerate(processes):
#             p.wait()

#             # Display returncode at failure
#             if p.returncode != 0:
#                 stdout, stderr = p.communicate()
#                 print(
#                     f"Execution of repertoire {i + j + 1}, {rep_batch[j]} failed with exit code {p.returncode}."
#                 )
#                 print(f"Out: \n{stdout}.")
#                 print(f"Error: \n{stderr}.")
