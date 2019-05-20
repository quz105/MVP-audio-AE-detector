#! /bin/bash

# Note: run this script in the directory where it locates such that two auxiliary python scripts, featureProcessing.py and trainAndtest.py, could be accessed easily.


# Function: for each of the four multiple-auxiliary-ASRs detection systems, DS0+{DS1, GCS}, DS0+{DS1, AT}, DS0+{GCS, AT}
#			and DS0+{DS1, GCS, AT}, train the deteciton system uing benign samples and a set of AEs (either blackbox AE
#			or whitebox AE), and then use it to detect another set of AEs unseen in the training process.
#
# Input:	the first parameter is the result directory
#			the second parameter is the directory that has all necessary transcriptions. Inside the directory, there are two sub-directories, "Train" and "unseenAEs"	
#			the third parameter is the directory that will be created to hold calculated similarity scores and feature vectors
#	
# Output:	for each multiple-auxiliary-ASRs detection system, false negative cases will be recorded in a file and detection result will be put in another file,
#			Furthermore, a result summary that records the detection results of all four systems is generated.

# Input Parameter #
result_dir=$(echo $1 | sed 's|/$||')
transcript_dir=$(echo $2 | sed 's|/$||')
scores_and_feature_vectors_dir=$(echo $3 | sed 's|/$||')

# Parameter Configuration #
working_dir=$(pwd)
cal_script="$working_dir/mam-similarity_score_calculation.py"
featuregenerationscript="$working_dir/featureProcessing.py"
train_and_test_script="$working_dir/mam_trainAndtest.py"
sim_cal_id="PhoneticEncodedJaroWinkler"
train_transcriptions_dir=$transcript_dir/Train
unseenAE_transcriptions_dir=$transcript_dir/unseenAEs
AETranscriptions=recogAETexts # common filename for AE transcriptions
BenignTranscriptions=recogBenignTexts # common filename for bening samples' transcriptions
## ASR models 
tm="DeepSpeech0.1.0" # target model
am1="DeepSpeech0.1.1" # aux model 1
am2="GoogleCloudSpeech" # aux model 2
am3="AmazonTranscribe" # aux model 3
## filepath: result summary
unseenAE_result_summary="$result_dir/UnseenAE_result_summary.txt"


# Clear result fold #
rm -rf "$result_dir"
mkdir -p "$result_dir"


# Calculation of Similarity Scores using Phonetic-encoded Jaro-winkler distance #
calculate_similarity_scores_between_two_models(){
	ASR_a=$1
	ASR_b=$2
	detectorsTag="$ASR_a"_"$ASR_b"

	echo -e "\n===Calculate similarity scores for $ASR_a vs $ASR_b==="

	echo -e "~~~Calculating: [AE dataset] for Training"
	python3 "$cal_script" "Yes" "Yes" "$detectorsTag" "$train_transcriptions_dir/$ASR_a/$AETranscriptions" "$train_transcriptions_dir/$ASR_b/$AETranscriptions" "$scores_and_feature_vectors_dir" "$sim_cal_id"

	echo -e "~~~Calculating: [Benign dataset] for Training"
	python3 "$cal_script" "No" "Yes" "$detectorsTag" "$train_transcriptions_dir/$ASR_a/$BenignTranscriptions" "$train_transcriptions_dir/$ASR_b/$BenignTranscriptions" "$scores_and_feature_vectors_dir" "$sim_cal_id"

	# For unseen AEs
	echo -e "~~~Calculating: [Unseen AEs] for testing"
	python3 "$cal_script" "Yes" "No" "$detectorsTag" "$unseenAE_transcriptions_dir/$ASR_a/$AETranscriptions" "$unseenAE_transcriptions_dir/$ASR_b/$AETranscriptions" "$scores_and_feature_vectors_dir" "$sim_cal_id"

	echo -e "===Calculation of Similarity Score for $ASR_a and $ASR_b: Done!===\n"

}

calculate_similarity_scores_between_two_models "$tm" "$am1"
calculate_similarity_scores_between_two_models "$tm" "$am2"
calculate_similarity_scores_between_two_models "$tm" "$am3"

# Feature Generation #
2-dim-feature_generation(){
## generate feature vectors
	fam1=$1
	fam2=$2
	sim_cal_id=$3
	AE_Train_Prefix="$scores_and_feature_vectors_dir/$sim_cal_id"_"AE_Train_$tm"
	Benign_Train_Prefix="$scores_and_feature_vectors_dir/$sim_cal_id"_"Benign_Train_$tm"
	AE_Unseen_Prefix="$scores_and_feature_vectors_dir/$sim_cal_id""_AE_Unseen_$tm"

	# for training
	echo -e "\tgenerating feature vectors for training"
	python3 "$featuregenerationscript" "$scores_and_feature_vectors_dir" "Yes" "Train" "$fam1"_"$fam2" "$sim_cal_id" "$AE_Train_Prefix"_"$fam1.txt" "$AE_Train_Prefix"_"$fam2.txt"
	python3 "$featuregenerationscript" "$scores_and_feature_vectors_dir" "No"  "Train" "$fam1"_"$fam2" "$sim_cal_id" "$Benign_Train_Prefix"_"$fam1.txt" "$Benign_Train_Prefix"_"$fam2.txt"

	# for unseen AEs
	echo -e "\tgenerating feature vectors for unseen AEs"
	python3 "$featuregenerationscript" "$scores_and_feature_vectors_dir" "Yes" "Unseen" "$fam1"_"$fam2" "$sim_cal_id" "$AE_Unseen_Prefix"_"$fam1.txt" "$AE_Unseen_Prefix"_"$fam2.txt"
}

3-dim-feature_generation(){
## generate feature vectors
	fam1=$1
	fam2=$2
	fam3=$3
	sim_cal_id=$4
	AE_Train_Prefix="$scores_and_feature_vectors_dir/$sim_cal_id"_"AE_Train_$tm"
	Benign_Train_Prefix="$scores_and_feature_vectors_dir/$sim_cal_id"_"Benign_Train_$tm"
	AE_Unseen_Prefix="$scores_and_feature_vectors_dir/$sim_cal_id""_AE_Unseen_$tm"

	# for training
	echo -e "\tgenerating feature vectors for training"
	python3 "$featuregenerationscript" "$scores_and_feature_vectors_dir" "Yes" "Train" "$fam1"_"$fam2"_"$fam3" "$sim_cal_id" "$AE_Train_Prefix"_"$fam1.txt" "$AE_Train_Prefix"_"$fam2.txt" "$AE_Train_Prefix"_"$fam3.txt"
	python3 "$featuregenerationscript" "$scores_and_feature_vectors_dir" "No"  "Train" "$fam1"_"$fam2"_"$fam3" "$sim_cal_id" "$Benign_Train_Prefix"_"$fam1.txt" "$Benign_Train_Prefix"_"$fam2.txt" "$Benign_Train_Prefix"_"$fam3.txt"

	# for unseen AEs
	echo -e "\tgenerating feature vectors for unseen AEs"
	python3 "$featuregenerationscript" "$scores_and_feature_vectors_dir" "Yes" "Unseen" "$fam1"_"$fam2"_"$fam3" "$sim_cal_id" "$AE_Unseen_Prefix"_"$fam1.txt" "$AE_Unseen_Prefix"_"$fam2.txt" "$AE_Unseen_Prefix"_"$fam3.txt"
}

feature_generation_with_PE_JW() {
	echo -e "\n===generating feature vectors calculated by $sim_cal_id==="
	echo "~~~Processing the case with two aux models: $am1 and $am2"
	2-dim-feature_generation "$am1" "$am2" "$sim_cal_id"
	echo "~~~Processing the case with two aux models: $am1 and $am3"
	2-dim-feature_generation "$am1" "$am3" "$sim_cal_id"
	echo "~~~Processing the case with two aux models: $am2 and $am3"
	2-dim-feature_generation "$am2" "$am3" "$sim_cal_id"
	echo "~~~Processing the case with three aux models: $am1 and $am2 and $am3"
	3-dim-feature_generation "$am1" "$am2" "$am3" "$sim_cal_id"
	echo -e "===feature generation finished===\n"
}

## generate all 2-aux-models and 3-aux-models feature vectors 
feature_generation_with_PE_JW


# training and testing #
train_and_test_one_system_with_one_cal(){
	aux_models_tag=$1
	sim_cal_id=$2
	AE_Train_Prefix="$scores_and_feature_vectors_dir/feature_vectors_$sim_cal_id""_AE_Train"
	Benign_Train_Prefix="$scores_and_feature_vectors_dir/feature_vectors_$sim_cal_id""_Benign_Train"
	AE_Unseen_Prefix="$scores_and_feature_vectors_dir/feature_vectors_$sim_cal_id""_AE_Unseen"
	
	echo -e "\tTrainging and Testing with aux models, $aux_models_tag and similarity calculation ID, $sim_cal_id"
	python3 "$train_and_test_script" "$AE_Train_Prefix"_"$aux_models_tag.txt" "$Benign_Train_Prefix"_"$aux_models_tag.txt" "$aux_models_tag" "$sim_cal_id" "$AE_Unseen_Prefix"_"$aux_models_tag.txt" "$result_dir" 
	echo "$sim_cal_id-$aux_models_tag# "$(cat "$result_dir/UnseenAE_result_$sim_cal_id"_"$aux_models_tag.txt") >> "$unseenAE_result_summary"
}

train_and_test_all_systems_with_one_sim_cal(){
	echo -e "\n===Train detection systems and test with unseen AEs==="

	echo "~~~Testing detection system built upon the target ASR $tm, and auxiliary ASRs, $am1 and $am2."
	train_and_test_one_system_with_one_cal "$am1"_"$am2" "$sim_cal_id"

	echo "~~~Testing detection system built upon the target ASR $tm, and auxiliary ASRs, $am1 and $am3."
	train_and_test_one_system_with_one_cal "$am1"_"$am3" "$sim_cal_id"

	echo "~~~Testing detection system built upon the target ASR $tm, and auxiliary ASRs, $am2 and $am3."
	train_and_test_one_system_with_one_cal "$am2"_"$am3" "$sim_cal_id"

	echo "~~~Testing detection system built upon the target ASR $tm, and auxiliary ASRs, $am1, $am2 and $am3."
	train_and_test_one_system_with_one_cal "$am1"_"$am2"_"$am3" "$sim_cal_id"

	echo -e "===Done!===\n"
}

train_and_test_all_systems_with_one_sim_cal

