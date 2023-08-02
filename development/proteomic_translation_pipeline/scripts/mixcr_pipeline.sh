# ==================================================== #
# This file contains example MiXCR commands 
# that I have used in the past to extract peptide 
# repertoires from paired-end read data sets
# ==================================================== #

mixcr analyze generic-amplicon \
    --species hs \
    --rna \
    --floating-left-alignment-boundary \
    --floating-right-alignment-boundary C \
    --drop-non-CDR3-alignments \
    --assemble-contigs-by CDR3 \
    --export-productive-clones-only \
    --impute-germline-on-export \
    --drop-default-fields \
    --append-export-clones-field readCount \
    --append-export-clones-field qFeature VDJRegion \
    --append-export-clones-field aaFeatureImputed VDJRegion \
    --append-export-clones-field nFeatureImputed VDJRegion \
    SRR8235277_R1.fastq \
    SRR8235277_R2.fastq \
	results \ 


# this is the one I need
mixcr analyze generic-amplicon \
    --species hs \
    --rna \
    --floating-left-alignment-boundary \
    --floating-right-alignment-boundary C \
    --drop-non-CDR3-alignments \
    --assemble-contigs-by VDJRegion \
    --drop-default-fields \
    --export-productive-clones-only \
    --impute-germline-on-export \
    --append-export-clones-field -cloneId \
    --append-export-clones-field -readCount \
    --append-export-clones-field -aaFeatureImputed VDJRegion \
    --append-export-clones-field -nFeatureImputed VDJRegion \
    SRR8235277_R1.fastq \
    SRR8235277_R2.fastq \


# this one works
mixcr analyze generic-amplicon \
    --species hs \
    --rna \
    --floating-left-alignment-boundary \
    --floating-right-alignment-boundary C \
    --drop-non-CDR3-alignments \
    --assemble-contigs-by VDJRegion \
    --drop-default-fields \
    --export-productive-clones-only \
    --impute-germline-on-export \
    --append-export-clones-field -cloneId \
    --append-export-clones-field -readCount \
    --append-export-clones-field -aaFeatureImputed VDJRegion \
    --append-export-clones-field -nFeatureImputed VDJRegion \
    SRR8235277_R1.fastq \
    SRR8235277_R2.fastq \



# these three are perfect but more work
mixcr analyze generic-amplicon \
    --species hs \
    --rna \
    --floating-left-alignment-boundary \
    --floating-right-alignment-boundary C \
    --drop-non-CDR3-alignments \
    --assemble-contigs-by VDJRegion \
    --remove-step exportClones \
    SRR8235277_R1.fastq \
    SRR8235277_R2.fastq \
    results

# concise
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

# verbose
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


