import os
import sys
import time
import shutil
import sqlite3
import argparse
import subprocess


parser = argparse.ArgumentParser(description="directory set up and MiXCR pipeline")

# Arguments
parser.add_argument("data_path", type=str, help="path to data directory") # /data/jgray21/iriver11/characterizing_bnabs/data 
parser.add_argument("--dataset", dest="dataset", type=str, default="RV217_40512", help="name of data set")
parser.add_argument("-c", "--chains", dest="chains", nargs='+', type=str, default=["IGK", "IGM", "IGG", "IGL"], help="chains expected in the data set")
parser.add_argument("--fields", dest="fields", nargs="+", type=str, default=["day"], help="additional database fields + DEFAULT repertoire path")
parser.add_argument("--skip-directory", dest="skip_directory", action="store_true", help="skip directory set up & downloads, only MiXCR pipeline")
parser.add_argument("-d", "--download-list", dest="download_list", type=str, default="download-list.txt", help="txt of .fastq files to download")
parser.add_argument("-m", "--mode", dest="mixcr_mode", type=str, default="CONCISE", help="exportClones mode is either CONCISE or VERBOSE")
args = parser.parse_args()

data_dir = args.data_path
data_set = args.dataset
chains = args.chains
fields = ["repertoire", "chain"] + args.fields 
skip_directory = args.skip_directory
download_list = args.download_list
mixcr_mode = args.mixcr_mode


# Path to Directories
data_set_dir = os.path.join(data_dir, data_set)
raw_data_dir = os.path.join(data_set_dir, "raw")
clones_data_dir = os.path.join(data_set_dir, "clones")


def download_with_aria(d_list):

    command = ["aria2c", "--console-log-level=error", "--download-result=hide", 
               "-c", "-s", "16", "-x", "16", "-k", "1M", "-j", "8", "-i", d_list]
    
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=raw_data_dir, text=True)
    process.wait()
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


if not skip_directory:

    # Create directory
    os.mkdir(data_set_dir)
    os.mkdir(raw_data_dir)
    os.mkdir(clones_data_dir)
    shutil.move(download_list, raw_data_dir)
    

    # Download all files into the raw directory
    max_tries = 10
    for i in range(max_tries):
        sys.stdout.write("Downloading...")
        exit_code, stdout, stderror = download_with_aria(download_list)
        if exit_code == 0:
            sys.stdout.write("\nDownload succesful.")
            break
        else:
            sys.stdout.write(f"\nDownload attempt {i + 1} failed with exit code: {exit_code}.")
            sys.stdout.write(f"{stdout}")
            time.sleep(5)
    
    if exit_code != 0:
        raise Exception("Download failed.")
    


# Data cleaning and store files in clones directory
connect = sqlite3.connect(data_set_dir)
fields_query = str()
for f in fields:
    fields_query += f"{f} TEXT NOT NULL,"

# Create a sqlite3 database
with connect.cursor() as cursor:
    cursor.execute(f"""
        CREATE TABLE repertoire (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {fields_query}
        ) 
    """)

connect.commit()

# Iterate through directory
repertoires = os.listdir(raw_data_dir)
insert = list()
for i, rep in enumerate(repertoires):
    
    rep_fields = rep.split("_")
    rep_insert = [rep]

    for r in rep_fields:
        for f in fields:
            if f in r:
                rep_insert.append(r.lower())
    
    insert.append(tuple(rep_insert))


# Insert into database
insert_query = ", ".join(fields)

with connect.cursor() as cursor:
    cursor.executemany(f""" 
        INSERT INTO repertoire ({insert_query})
        VALUES ({("?,"*len(fields)).rstrip(",")})
    """,
    insert)

connect.close()


# Execute MiXCR_analyze command (in batches of 6)
def MiXCR_analyze(repertoires, batch_size = 6):


    # Run alignment + assemble
    for i in range(0, len(repertoires), batch_size):
        
        rep_batch = repertoires[i:i + batch_size]
        
        processes = list()

        for rep in rep_batch:

            rep_dir = os.path.join(raw_data_dir, rep)

            MiXCR = ["mixcr", "analyze", "generic-amplicon", "--species", "hs", "--rna", 
                       "--floating-left-alginment-boundary", "--floating-right-alignment-boundary", "C", 
                       "--drop-non-CDR3-alignments", "--assemble-contigs-by", " VDJRegion", "--remove-step", "exportClones", 
                       f"{rep}_R1.fastq", f"{rep}_R2.fastq", f"{rep}_clones"]

            process = subprocess.Popen(MiXCR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=rep_dir, text=True)
            processes.append(process)

        for p in processes:
            p.wait()


# Execute MiXCR_export command (in batches of 12)
def MiXCR_export(repertoires, batch_size = 12):

    # Run exportClones
    for i in range(0, len(repertoires), batch_size):
        
        rep_batch = repertoires[i:i + batch_size]
        
        processes = list()

        for rep in rep_batch:
            
            rep_dir = os.path.join(raw_data_dir, rep)
            rep_clones_dir = os.path.join(clones_data_dir, rep, f"{rep}_clones.tsv")

            MiXCR = ["mixcr", "--export-productive-clones-only", "--impute-germline-on-export", "--drop-default-fields", 
                        "--chains IGK", "-cloneId", "-readCount", "-aaFeatureImputed VDJRegion", "-nFeatureImputed VDJRegion", 
                        f"{rep}_clones.clns", f"{rep_clones_dir}"]

            
            process = subprocess.Popen(MiXCR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=rep_dir, text=True)
            processes.append(process)

        for p in processes:
            p.wait()


# Execute MiXCR Pipeline
MiXCR_analyze(repertoires=repertoires)
MiXCR_export(repertoires=repertoires)
