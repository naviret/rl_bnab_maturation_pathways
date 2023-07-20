import os
import sys
import glob
import time
import shutil
import argparse
import subprocess


parser = argparse.ArgumentParser(description="directory set up and MiXCR pipeline")

# Arguments
parser.add_argument("data_path", type=str, help="path to data directory") # /data/jgray21/iriver11/ 
parser.add_argument("--data-set", "--data-set", dest="data_set", type=str, default="RV217_40512", help="name of data set")
parser.add_argument("-c", "--chains", dest="chains", nargs='+', type=str, default=["IGK", "IGM", "IGG", "IGL"], help="chains expected in the data set")
parser.add_argument("--skip-directory", dest="skip_directory", action="store_true", help="skip directory set up & downloads, only MiXCR pipeline")
parser.add_argument("-d", "--download-list", dest="download_list", type=str, default="download-list.txt", help="txt of .fastq files to download")
parser.add_argument("-m", "--mode", dest="mixcr_mode", type=str, default="CONCISE", help="exportClones mode is either CONCISE or VERBOSE")
args = parser.parse_args()

data_dir = args.data_path
data_set = args.data_set
chains = args.chains
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
        sys.stdout.write("\nDownloading...")
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
"""
repertoires = list()
for rep in os.listdir(raw_data_dir):
    for c in chains:
        if c.lower() in rep.lower():
            if not c in repertoires.keys():
                
"""