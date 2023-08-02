# colabfold command
colabfold_batch $FASTA_DIR $OUTPUT_DIR \
    --model-type alphafold2_multimer_v3 \
    --msa-mode mmseqs2_uniref \
    --amber \
    --num-relax 3 \
    --num-recycle 20 \
    --recycle-early-stop-tolerance 0.5 \
    --custom-template-path \
    --pair-mode unpaired \
    --use-gpu-relax \
    