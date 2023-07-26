import io
import os
import sys
import esm
import time
import torch
import shutil
import sqlite3
import argparse
import subprocess
import numpy as np
import pandas as pd
from datetime import datetime
from sqlite3 import OperationalError



parser = argparse.ArgumentParser(description="sequence selection pipeline")

# Arguments
parser.add_argument("data_path", type=str, help="path to data directory") # /data/jgray21/iriver11/characterizing_bnabs/data 
parser.add_argument("--dataset", "--dataset", dest="data_set", type=str, default="RV217_40512", help="name of data set")
parser.add_argument("--database", dest="database", type=str, help="path to sqlite database")
parser.add_argument("--scratch-directory", dest="scratch_directory", type=str, help="path to scratch directory (for temorary files)")  # scratch16
parser.add_argument("--selection-critera", dest="selection_critera", nargs="+", type=str, default=["day:day240", "chain:igh"], help="selection criteria formatted as <select:value>")
args = parser.parse_args()

data_dir = args.data_path
dataset = args.dataset
database = os.path.join(data_dir, dataset) if args.database == None else args.database
scratch_dir = args.scratch_directory
selection_criteria = args.selection_critera ##### [FUTURE DEV] #####


# Path to Directories
data_set_dir = os.path.join(data_dir, dataset)
clones_data_dir = os.path.join(data_set_dir, "clones")
temp_scratch_dir = os.path.join(scratch_dir, f"{dataset}/seq_pred_temp")
input_scratch_dir = os.path.join(temp_scratch_dir, "input")
output_scratch_dir = os.path.join(temp_scratch_dir, "output")


# Extracting selection from database
def select_from_database(database, selection_criteria):

    # Connect to database
    with sqlite3.connect(database) as connect:

        # Prepare a query
        constraints = list()
        for selection in selection_criteria:
            select, value = selection.split(":")
            constraints.append(f"repertoire.{select} = {value}")

        query = f"""
            SELECT *
            FROM sequence
            JOIN repertoire ON sequence.repertoire_address = repertoire.repertoire_address 
            WHERE {" AND ".join(constraints)}
        """

        # Query database
        results = pd.read_sql_query(query, connect)

    return results


selected = select_from_database(database, selection_criteria)

# Only if there are peptide sequence, proceed
if "aaSeqImputedVDJRegion" not in selected.columns:
    raise OperationalError(f"Peptide column (aaSeqImputedVDJRegion) was not found.")


# Build fasta
def predict_structures(data, batch_size = 15):

    extract = ["id", "repertoire_address", "aaSeqImputedVDJRegion"]
    entries = selected[extract].to_numpy().tolist
    number_of_seqs = len(entry)

    id_idx = extract.index("id")
    rep_address_idx = extract.index("repertoire_address")
    aa_seq_idx = extract.index("aaSeqImputedVDJRegion")

    for i in range(0, number_of_seqs, batch_size):
        
        batch = entries[i:i + batch_size]
        batch_path = os.path.join(input_scratch_dir, get_job_name(i))

        # Write fasta file
        with open(batch_path, 'w') as fasta:
            
            for entry in batch:

                seq_id = entry[id_idx]
                rep_address = entry[rep_address_idx]
                peptide_seq = entry[aa_seq_idx]

                print(f">{rep_address}@{seq_id}", file=fasta)
                print(f"{peptide_seq}", file=fasta)

        # Submit the job
        



        

# Get current date (for job name)
def get_job_name(job_num, max=4):

    # Get current date and time
    date = datetime.now()

    # Format the name 
    job_name = f"seq_pred_{date:%b%d}_job#{job_num+1:0{max}}.fasta".lower()
    
    return job_name

### build fasta files using database (10 sequences per file)
### Remember to put in scratch directory
### Create job per fasta file
### Submit jobs







# query = f"""
#             SELECT *
#             FROM sequence
#             WHERE repertoire_address IN (
#                 SELECT repertoire_address
#                 FROM repertoire
#                 WHERE {" AND ".join(constraints)}
#             )
#         """
