import os
import sys
import time
import shutil
import sqlite3
import argparse
import subprocess
import numpy as np
import pandas as pd


parser = argparse.ArgumentParser(description="directory set up and MiXCR pipeline")

# Arguments
parser.add_argument("data_path", type=str, help="path to data directory") # /data/jgray21/iriver11/characterizing_bnabs/data 
parser.add_argument("--dataset", "--dataset", dest="data_set", type=str, default="RV217_40512", help="name of data set")
parser.add_argument("--database", dest="database", type=str, help="path to sqlite database")  
parser.add_argument("-peptide", dest="peptide", action="store_true", help="obtain peptide (amino acid) sequences")  
parser.add_argument("-nucleotide", dest="nucleotide", action="store_true", help="obtain nucleotide sequences")  
parser.add_argument("--selection-critera", dest="selection_critera", nargs="+", type=str, default=["day:day240", "chain:igh"], help="selection criteria formatted as <select:value>")
parser.add_argument("-cluster", dest="cluster", action="store_true", help="extract representatives from clusters, otherwise extract random")
parser.add_argument("--sample-size", dest="sample_size", type=int, default=1000, help="number of sequences to extract")
args = parser.parse_args()

if not (args.peptide or args.nucleotide):
    parser.error("no sequence type requested, add -peptide or -nucleotide or both")

data_dir = args.data_path
data_set = args.dataset
database = os.path.join(data_dir, data_set) if args.database == None else args.database
peptide = args.peptide
nucleotide = args.nucleotide 
selection_criteria = args.selection_critera ##### [FUTURE DEV] #####
cluster = args.cluster ##### [FUTURE DEV] #####
sample_size = args.sample_size


# Path to Directories
data_set_dir = os.path.join(data_dir, data_set)
clones_data_dir = os.path.join(data_set_dir, "clones")


# Extracting selection from database
def select_from_database(database, selection_criteria):

    # Connect to database
    with sqlite3.connect(database) as connect:

        # Prepare a query
        constraints = fields = str()
        for selection in selection_criteria:
            select, value = selection.split(":")
            constraints += f"{select}={value}"

        query = f"""
            SELECT *
            FROM repertoire
            WHERE {fields.rstrip(" AND")}
        """

        # Query database
        results = pd.read_sql_query(query, connect)

    return results


selected = select_from_database(database, selection_criteria)



# Create new table in database for sequences

# Extract all nucleotide or amino acid sequences or BOTH
extract = list()
if peptide:
    extract.append("aaSeqImputedVDJRegion")
if nucleotide:
    extract.append("nSeqImputedVDJRegion")

fields_query = str()
for e in extract:
    fields_query += f"{e} TEXT NOT NULL,"

fields_query += "embedding BLOB"


# Create a sqlite3 database
with sqlite3.connect(database) as connect:
    with connect.cursor() as cursor:
        cursor.execute(f"""
            CREATE TABLE repertoire (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {fields_query},
            ) 
        """)

    connect.commit()





# Identify files to be read
repertoires = selected["repertoire"]
for rep in repertoires:
    
    rep_dir = os.path.join(clones_data_dir, rep, f"{rep}_clones.tsv")
    clones = pd.read_table(rep_dir, sep="\t")

    # Sequence selection (random)
    seqs = clones[extract].to_numpy()
    
    # Shuffle rows
    np.random.shuffle(seqs)

    # Extract sample size 
    seqs = seqs[:sample_size] 

    # Generate ESM-2 embeddings for protein sequences
    if peptide: 
        idx = extract.index("aaSeqImputedVDJRegion")
        peptide_seqs = seqs[:, idx]

        






def ESM2_embed()




