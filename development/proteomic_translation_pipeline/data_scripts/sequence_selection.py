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
from esm.data import BatchConverter



parser = argparse.ArgumentParser(description="sequence selection pipeline")

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
        constraints = list()
        for selection in selection_criteria:
            select, value = selection.split(":")
            constraints.append(f"{select} = {value}")

        query = f"""
            SELECT *
            FROM repertoire
            WHERE {" AND ".join(constraints)}
        """

        # Query database
        results = pd.read_sql_query(query, connect)

    return results


selected = select_from_database(database, selection_criteria)



# Create new table in database for sequences

# Extract all nucleotide or amino acid sequences or BOTH
extract = list(["repertoire_address"])
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
            CREATE TABLE sequence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {fields_query},
                FOREIGN KEY (repertoire_address) REFERENCES reperetoire(repertoire_address)
            ) 
        """)

    connect.commit()


# Generate ESM-2 embeddings
def ESM2_embed(data):
    
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()  # disables dropout for deterministic results

    batch_converter = MyBatchConverter(alphabet=alphabet)
    labels, batch_strs, batch_tokens = batch_converter(data)
    batch_lens = (batch_tokens != alphabet.padding_idx).sum(1)

    # Extract per-residue representations (on CPU)
    with torch.no_grad():
        results = model(batch_tokens, repr_layers=[33], return_contacts=True)
    token_representations = results["representations"][33]

    # Extract sequence representations
    sequence_representations = []
    for i, tokens_len in enumerate(batch_lens):
        sequence_representations.append(token_representations[i, 1 : tokens_len - 1].mean(0))

    return sequence_representations


# Insert into database
insert_query = ", ".join(extract + ["embedding"])

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

    # Generate ESM-2 embeddings for protein sequences only
    if peptide: 
        idx = extract.index("aaSeqImputedVDJRegion")
        peptide_seqs = np.char.upper(seqs[:, idx]).tolist()
        
        seq_embedddings = ESM2_embed(peptide_seqs)

    insert = list()
    for entry, embedding in zip(seqs.tolist(), seq_embedddings):
        
        # Insert repertoire address
        entry.insert(0, rep)

        # Serializing tensor
        buffer = io.BytesIO()
        torch.save(embedding, buffer)

        # Adding buffer as a column
        entry.append(buffer.getvalue())

        # Insert query for sqlite3 database
        insert.append(tuple(entry))

    # Execute query
    with sqlite3.connect(database) as connect:
        with connect.cursor() as cursor:
            cursor.executemany(f""" 
                INSERT INTO sequence ({insert_query})
                VALUES ({("?,"*(len(extract) + 1)).rstrip(",")})
            """,
            insert)

        connect.commit()



# ESM-2 BatchConverter class with some modifications
class MyBatchConverter(BatchConverter):
    
    def __init__(self, alphabet, labels: bool = False, truncation_seq_length: int = None):
        super().__init__(alphabet=alphabet, truncation_seq_length=truncation_seq_length)
        self.label = False

    def __call__(self, raw_batch):

        if not self.label:
            raw_batch = [(f"id{i}", seq_str) for i, seq_str in enumerate(raw_batch)]

        labels, strs, tokens = super().__call__(raw_batch)
        return labels, strs, tokens
    


"""
##### [FUTURE DEV] #####
selection_criteria = args.selection_critera 

    If there is more than one query then we need to allow for more than one selection criteria to be taken,
    this can be done with a txt file while each row is the selection criteria for one query


"""