# ==================================================== #
# This file contains notes on development and 
# future additions to my work pipelines
# ==================================================== #

"""
##### [GENERAL FUTURE DEV] #####
I should create a separate file for all the sqlite3 functions that I've created. I've started to
reuse them in other files so it'll be better if I don't have to keep copying them   
It would be cool if I could make a class called sqliteAPI that can instantiate the database and
use all of the functions

"""

""" ========================================= sequence_selection.py

##### [FUTURE DEV] ##### {0003}
Option read both paired end PCR reads and single seq PCR reads

##### [FUTURE DEV] ##### {0004}
MiXCR mode option. MiXCR commands allows default columns for exportClones for more information.
    Two options (self-explanatory):
    - CONCISE (already developed)
        """
            mixcr exportClones \
                --export-productive-clones-only \
                --impute-germline-on-export \
                --drop-default-fields \
                --chains IGK \
                -cloneId \
                -readCount \
                -aaFeatureImputed VDJRegion \
                -nFeatureImputed VDJRegion \
                clones.clns clones.tsv
        """

    - VERBOSE (missing)
        """
            mixcr exportClones \
                --export-productive-clones-only \
                --impute-germline-on-export \
                --drop-default-fields \
                --chains IGK \
                -cloneId \
                -readCount \
                -vGene \
                -dGene \
                -jGene \
                -aaFeatureImputed VDJRegion \
                -nFeatureImputed VDJRegion \
                -aaFeatureImputed VDJRegion+CRegion \
                -nFeatureImputed VDJRegion+CRegion \
                clones.clns clones.tsv
        """


"""


""" ========================================= sequence_selection.py

##### [FUTURE DEV] ##### {0001}
selection_criteria = args.selection_critera 

    If there is more than one query then we need to allow for more than one selection criteria to be taken,
    this can be done with a txt file while each row is the selection criteria for one query
    - This will make use of functions I've already set up to iterate through txt.
    - Find better way to organize these functions with auxilliary files? 
 
##### [FUTURE DEV] ##### {0002}
Option to k-means cluster rather than randomly choosing some sequences.

"""


""" ========================================= structure_prediction.py

##### [FUTURE DEV] ##### {0001}
selection_criteria = args.selection_critera 

    If there is more than one query then we need to allow for more than one selection criteria to be taken,
    this can be done with a txt file while each row is the selection criteria for one query.
    - This will make use of functions I've already set up to iterate through txt.
    - Find better way to organize these functions with auxilliary files? 

##### [USEFUL CMDS] #####
This can be used for sequence selection 

query = f"""
            SELECT *
            FROM sequence
            WHERE repertoire_address IN (
                SELECT repertoire_address
                FROM repertoire
                WHERE {" AND ".join(constraints)}
            )
        """

"""


        