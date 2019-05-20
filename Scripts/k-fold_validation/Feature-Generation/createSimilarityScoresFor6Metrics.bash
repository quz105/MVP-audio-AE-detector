#! /bin/bash

# Function: calculate simlarity scores of transcriptions recognized by target ASR (DeepSpeech v0.1.0)
#			and corresponding transcriptions recognized by three auxiliary ASRs. Six similarity metrics
#			are used.
#
# Input   : the first paramter is the result directory
#		  : the second parameter is the directory that contains all necessary transcriptions
#
# Output  : inside result directory, four sub-directories (ss_AE_Test, ss_AE_Train, ss_Benign_Test and ss_Benign_Train)
#		  : will be created. In each of them, 18 similarity scores files are generated. Each of these 18
#		  : files contains similarity scores (calculated by one of the 6 similarity metric) between transcriptions
#		  : recognized by the target ASR and one of the three auxiliary ASRs.

result_dir=$(echo "$1" | sed -e 's|/$||')
transcriptionDir=$(echo "$2" | sed -e 's|/$||')

cal_script="similarityScoresCalWith3AuxASRs.sh"
sim_cal_ids=(PhoneticEncodedJaroWinkler)
#sim_cal_ids=(Jaccard Cosine JaroWinkler PhoneticEncodedJaccard PhoneticEncodedCosine PhoneticEncodedJaroWinkler)


# A combination of (AEType, dsType) is one type.
# There are 4 types: (AE, Test), (Benign, Test), (AE, Train) and (Benign, Train)
sim_cal_for_one_type(){
	AEType=$1
	dsType=$2
	tDir="$transcriptionDir/$dsType" # transcription directory
	rDir="$result_dir/ss_$AEType""_$dsType" # result directory
	tComFile="recog$AEType""Texts" # transcripition filename, either "recogAETexts" or "recogBenignTexts"

	for sim_cal_id in ${sim_cal_ids[*]}
	do
		"./$cal_script" "$rDir" "$sim_cal_id" "$AEType" "$dsType" "$tDir" "$tComFile"
	done
}

sim_cal_for_one_type AE Test
sim_cal_for_one_type Benign Test
sim_cal_for_one_type AE Train
sim_cal_for_one_type Benign Train

