#!/bin/bash

# Function: for each of the three single-auxiliary-ASR detection systems, DS0+{DS1}, DS0+{GCS} and DS0+{AT},
#			use all benign samples to train the system, and then test the system with all AEs.
#
# Input:	the first parameter is the root directory that holds all the unseeen-AE-attack experimental results
#			the second parameter is the prefix of directory name, which holds experimental result for a given FPR.
#			the third parameter is the given maximum FPR
#			the four parameter is the directory that holds all necessary transcriptions
#
# Output:	a directory named <second parameter>_givenFPR<the third parameter>, for example, unseenAEs_givenFPR0.05,
#			will be generated inside the root directory indicated by the first parameter. All experimental result
#			for the given FPR are stored inside this newly created directory.

result_root_dir=$(echo $1 | sed 's|/$||')
result_dir_name_pre=$2
givenFPR=$3
transcriptions_dir=$(echo $4 | sed 's|/$||')

result_dir="$result_root_dir"/"$result_dir_name_pre""_givenFPR$givenFPR"
train_transcriptions_dir="$transcriptions_dir"/Train
unseenAE_transcriptions_dir="$transcriptions_dir"/unseenAEs

rm -rf "$result_dir"

train_and_test_script=1am_trainAndtest.py
target_ASR=DeepSpeech0.1.0
aux_ASR1=DeepSpeech0.1.1
aux_ASR2=GoogleCloudSpeech
aux_ASR3=AmazonTranscribe



train_and_test_with_1_aux_model(){
	aux_ASR=$1
	echo -e "\n[Experiment on $target_ASR vs $aux_ASR]"
	python3	"$train_and_test_script" "$target_ASR" "$aux_ASR" \
			"${unseenAE_transcriptions_dir}/${target_ASR}/recogAETexts" "${unseenAE_transcriptions_dir}/${aux_ASR}/recogAETexts" \
			"${train_transcriptions_dir}/${target_ASR}/recogBenignTexts" "${train_transcriptions_dir}/${aux_ASR}/recogBenignTexts" \
			"$result_dir" "$givenFPR"
	echo -e "[Experiment is done]\n"

}

train_and_test_with_1_aux_model "$aux_ASR1"
train_and_test_with_1_aux_model "$aux_ASR2"
train_and_test_with_1_aux_model "$aux_ASR3"
