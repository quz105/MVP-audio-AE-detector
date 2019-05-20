#!/bin/bash

# Function:	for each dataset, all necessary feature-vector files for experiments of
#		single-auxiliary-ASR and multiple-auxiliary-ASRs detection systems will be created
#		and placed in the directory named "feacture_vectors"

DATASET_ROOT=$(echo "$1" | sed -e 's|/$||')
k=$2

currentK="1"
while [ "$currentK" -le "$k" ]
do
    RESULT_DIR="$DATASET_ROOT"/"$currentK"
    TRANSCRIPTIONS_DIR=$RESULT_DIR

    # Generate similarity scores
    echo -e "\n[Generate similarity scores]"
    ./createSimilarityScoresFor6Metrics.bash "$RESULT_DIR" "$TRANSCRIPTIONS_DIR"

    # Generate feature vectors
    echo -e "\n[Generate feature vectors]"
    ./createFeatureVectors.bash "$RESULT_DIR"

    currentK=$[$currentK+1]
done
