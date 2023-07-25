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
parser.add_argument("--scratch-directory", dest="scratch_directory", type=str, help="path to scratch directory (for temorary files)")    
parser.add_argument("--selection-critera", dest="selection_critera", nargs="+", type=str, default=["day:day240", "chain:igh"], help="selection criteria formatted as <select:value>")
args = parser.parse_args()


### build fasta files using database
### Remember to put in scratch directory
### Create job per fasta file
### Submit jobs

