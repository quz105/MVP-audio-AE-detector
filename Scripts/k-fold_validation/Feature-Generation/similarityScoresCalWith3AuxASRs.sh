#!/bin/bash

result_dir=$1
sim_cal_id=$2
AEType=$3 # AE or Benign
dsType=$4 # Train, Test or Stress
transcriptionDir=$5
transcriptionCommonFilename=$6

if [ "$sim_cal_id" != "Jaccard" ] && [ "$sim_cal_id" != "Cosine" ] && [ "$sim_cal_id" != "JaroWinkler" ] && [ "$sim_cal_id" != "PhoneticEncodedJaccard" ] && [ "$sim_cal_id" != "PhoneticEncodedCosine" ] && [ "$sim_cal_id" != "PhoneticEncodedJaroWinkler" ]
then
	echo "the input of ID of similarity calculation is invalid. Please select one of the follow three."
	echo "(1) Jaccard"
	echo "(2) Cosine"
	echo "(3) JaroWinkler"
	echo "(4) PhoneticEncodedJaccard"
	echo "(5) PhoneticEncodedCosine"
	echo "(6) PhoneticEncodedJaroWinkler"
	exit 1
fi

echo "Similairty Calculation Method Used: $sim_cal_id" 

ASR1=DeepSpeech0.1.0
ASR2=DeepSpeech0.1.1
ASR3=GoogleCloudSpeech
ASR4=AmazonTranscribe


cal_script=similarity_score_calculation.py


calculate_similarity_scores_between_two_models(){
	ASR_a=$1
	ASR_b=$2
	AEType=$3
	dsType=$4
	recogFP1=$5
	recogFP2=$6

	echo -e "\nCalculate similarity scores for $ASR_a vs $ASR_b"
	echo -e "Calculating: AE dataset ($AEType), Training part ($dsType)"
	python3 "$cal_script" "$AEType" "$dsType" "$ASR_a"_"$ASR_b" "$recogFP1" "$recogFP2" "$result_dir" "$sim_cal_id"
	echo -e "Done!\n"
}

calculate_similarity_scores_between_two_models "$ASR1" "$ASR2" "$AEType" "$dsType" "$transcriptionDir/$ASR1/$transcriptionCommonFilename" "$transcriptionDir/$ASR2/$transcriptionCommonFilename"
calculate_similarity_scores_between_two_models "$ASR1" "$ASR3" "$AEType" "$dsType" "$transcriptionDir/$ASR1/$transcriptionCommonFilename" "$transcriptionDir/$ASR3/$transcriptionCommonFilename"
calculate_similarity_scores_between_two_models "$ASR1" "$ASR4" "$AEType" "$dsType" "$transcriptionDir/$ASR1/$transcriptionCommonFilename" "$transcriptionDir/$ASR4/$transcriptionCommonFilename"


