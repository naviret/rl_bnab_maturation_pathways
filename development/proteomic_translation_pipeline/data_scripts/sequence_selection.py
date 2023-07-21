import os
import sys
import time
import shutil
import sqlite3
import argparse
import subprocess
import pandas as pd


parser = argparse.ArgumentParser(description="directory set up and MiXCR pipeline")


# Arguments
parser.add_argument("data_path", type=str, help="path to data directory") # /data/jgray21/iriver11/characterizing_bnabs/data 
parser.add_argument("--dataset", "--dataset", dest="data_set", type=str, default="RV217_40512", help="name of data set")
parser.add_argument("--database", dest="database", type=str, help="path to sqlite database")  
parser.add_argument("--selection-critera", dest="selection_critera", nargs="+", type=str, default=["day:day240", "chain:igh"], help="selection criteria formatted as <select:value>")
parser.add_argument("--cluster", dest="cluster", action="store_true", help="extract representatives from clusters, otherwise extract random")
args = parser.parse_args()

data_dir = args.data_path
data_set = args.dataset
database = os.path.join(data_dir, data_set) if args.database == None else args.database
selection_criteria = args.selection_critera
cluster = args.cluster



def select_from_database(database, selection_criteria):

    # Connect to database
    with sqlite3.connect(database) as connect:

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
        with connect.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

    return results


selected = select_from_database(database, selection_criteria)

