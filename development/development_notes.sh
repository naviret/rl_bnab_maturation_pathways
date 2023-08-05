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

##### [FUTURE DEV] ##### {0005}
Only do structure prediction on variable regions of heavy chain and light chain.

    Need to figure out how to extract the variable region and remove the constant region

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



""" ================================ ROSETTA CON 2023 POSTER PRESENTATION

BACKGROUND:
- Affinity maturation (AM) is the proecss by which B cells evolve to produce antibodies with 
increased binding affinity, and thus, neutralizing activity, against some antigen [?].
    - The variational force driving the AM process is called hypersomatic mutation, which accumulates
    mutations in B cell receptors (BCRs) and selects those B cells with high neutralization activity
    against some antigen. 
- Broadly neutralizing antibodies (bnAbs) sometimes arise through AM by targetting conserved regions
in the antigen of interest. This confers //high neutralization breadth// against a number of subtypes 
of the same virus [?].
- As a result, broadly neutralizing antibodies have gained much interest due to their promise in fighting
some of the most variable, and consequently the most dangerous viruses in modern medicine. These include
HIV, Influenza, Coronavirus, and other Hepatitus viruses. [?]

MOTIVATION:
- Thus, given representation of the AM landscape for specific bnAb lineages, finding a way to optimally traverse
this landscape, ie. the features that standout in the pathway from germline to bnAb, 
can give insight into optimal vaccination protocols for these dangerous and highly variable pathogens.
- Gready search algorithms (like A*) and deep reinforcement learning approaches have been used in silico to optimize
vaccination strategies to elicit bnAbs, so there is promise in their ability to characterize bnAb AM pathways [?].

In this project we hope to:
- develop a graph representation of the AM landscape
- traverse this landscape using informed search algorithms and reinforcement learning

DATA:
Longitudinal dataset (Bio Project: PRJNA486355) of one patient who developed 
antibody lineages against the MPER epitope [?], a highly known
conserved region of the HIV-1 gp41 envelope protein [?].
- taken over 654 days after identification of Fiebig I infection stage
- discovered 3 bnAb lineages (VRC42, VRC43, VRC46) for a total of 9 antibodies
- unpaired heavy and light chain data
- NGS nucleotide sequences
- memory B cells

METHODS/AIMS:
1. [Check] Generate protein sequences from a DNA repretoire
    - Using MiXCR
    - Gene alignments
    - Found CDR regions and imputed best aligned gene hits
2. [Check] Extract representative protein sequences 
    - Embed sequences using ESM-2
        - Large protein language models can capture both functional 
        and structural properties of proteins, meaning that the resulting encoding 
        is well-informed and representative of the entire sequence and
        potential structure [13, 14]
    - Cluster sequences using embeddings.
        - Choose the most "centerered" sequences to be representatives of the cluster
            - This is determined by finding the sequence with the 
            smallest median Hamming distance from all other sequences in the cluster
    - Randomly choose protein sequences 
3. [Check] Build antibody-antigen structures using AF2
    - Antigen template 
    - Since unpaired heavy and light chain; pair all heavy chains 
    with template light chain and vice versa
        - heavy chain is more variable and has more 
        interactions with light chain 
    - Allow MSAs to build heavy chain and light chain
4. Build graph landscape
5. A* implementation using heuristics
    - Show the heuristic functions
6. Reinforcement learnign algorithm
    - Show the model architechture figure and REWARD FUNCTIONS 

EXPECTATIONS: 
- Reinforcement learning algorithm will find a policy that represents the decisions
made in the AM pathway
- Mapping the pathway using binding energy will show a general trend for decreasing 
binding energy BUT with some exceptions since we might have to go from a high affinity
antibody to a variable epitope to a lower affinity antidbody to a conserved epitope
- Expect graph for heavy chain to look be more varied 

"""






""" ========================================= buffer.py

##### [FUTURE DEV] ##### {0006}
The way it's set up now, 

    batch_size can't be bigger than memory_size --> implement a check for this

    once memory_counter is bigger than batch_size, we will always do learning even
    if only one more action is made BUT we still only choose randomly from all the tuples 
    that we have

        so what's the tradeoff here:
            1. keep training on every iteration with mostly old values in current case
            2. reset the memory_counter once the memory_size is surpassed then allow it 
            to generate MORE new samples before training again (so that we have the same number
            of samples as the batch size (at least))

                what does this mean?
                we are letting the policy be used more even though it
                might not be a good policy BUT we still keep most of the old
                values 

                ---> tradeoff is: more new samples (one batch worth of new samples) vs 
                only one new sample, this means less training overall (although easily solved by
                increasing the amount of episodes)

                    is it better that we will see more new MDP tuples or should we stick
                    with the older tuples?


"""