#! /bin/bash

# Function: based on similarity scores of transcription recognized by the target ASR (DeepSpeech v0.1.0) and transcriptions
#			recognized by the three auxiliary ASRs, generate 2-dimentional and 3-dimentional feature vectors for all 4 kinds
#			multiple-auxiliary-ASRs detection systems by using 6 similarity metric one by one.
#
# Input   :	the first parameter is the root directory of storing files of similairy scores and files of feature vectors
#
# Output  : four directories (fv_AE_Test, fv_AE_Train, fv_Benign_Test, fv_Benign_Train) are created to hold corresponding
#			files of feature vectors. Then, all files in these four directories are copied into the directory, feature_vectors.


working_dir=$(echo "$1" | sed -e 's|/$||')
score_dir_pre="ss_"
fv_dir_pre="fv_"
fv_dir="$working_dir"/"feature_vectors"

sample_tags=(AE_Test AE_Train Benign_Test Benign_Train)
sim_cal_ids=(PhoneticEncodedJaroWinkler)
#sim_cal_ids=(Jaccard Cosine JaroWinkler PhoneticEncodedJaccard PhoneticEncodedCosine PhoneticEncodedJaroWinkler)



tm="DeepSpeech0.1.0" # target model
am1="DeepSpeech0.1.1" # aux model 1
am2="GoogleCloudSpeech" # aux model 2
am3="AmazonTranscribe" # aux model 3

fgs="featureProcessing.py"


# Feature Generation #

# create 1-dimentional feacture vectors for one type dataset, which are consumed by detection systems with 2 auxiliary ASRs
1_dim_fv_generation_atomic(){
	fam1=$1 # first auxiliary ASR name
	sim_cal_id=$2
	AEType=$3
	dsType=$4
	sample_tag="$AEType""_""$dsType" # AE_Train, AE_Test, Benign_Train, Benign_Test and AE_Stress
	score_dir="$working_dir"/"$score_dir_pre""$sample_tag"
	result_dir="$working_dir"/"$fv_dir_pre""$sample_tag"
	fp_prefix="$score_dir"/"$sim_cal_id"_"$sample_tag"_"$tm"
	python3 "$fgs" "$AEType" "$dsType" "$fam1" "$sim_cal_id" "$result_dir" "$fp_prefix"_"$fam1.txt"
}

# create 2-dimentional feacture vectors for one type dataset, which are consumed by detection systems with 2 auxiliary ASRs
2_dim_fv_generation_atomic(){
	fam1=$1 # first auxiliary ASR name
	fam2=$2 # second auxiliary ASR name
	sim_cal_id=$3
	AEType=$4
	dsType=$5
	sample_tag="$AEType""_""$dsType" # AE_Train, AE_Test, Benign_Train, Benign_Test and AE_Stress
	score_dir="$working_dir"/"$score_dir_pre""$sample_tag"
	result_dir="$working_dir"/"$fv_dir_pre""$sample_tag"
	fp_prefix="$score_dir"/"$sim_cal_id"_"$sample_tag"_"$tm"
	python3 "$fgs" "$AEType" "$dsType" "$fam1"_"$fam2" "$sim_cal_id" "$result_dir" "$fp_prefix"_"$fam1.txt" "$fp_prefix"_"$fam2.txt"

}

# create 3-dimentional feacture vectors for one type dataset, which are consumed by detection systems with 3 auxiliary ASRs
3_dim_fv_generation_atomic(){
	fam1=$1 # first auxiliary ASR name
	fam2=$2 # second auxiliary ASR name
	fam3=$3 # third auxiliary ASR name
	sim_cal_id=$4
	AEType=$5
	dsType=$6
	sample_tag="$AEType""_""$dsType" # AE_Train, AE_Test, Benign_Train, Benign_Test and AE_Stress
	score_dir="$working_dir"/"$score_dir_pre""$sample_tag"
	result_dir="$working_dir"/"$fv_dir_pre""$sample_tag"
	fp_prefix="$score_dir"/"$sim_cal_id"_"$sample_tag"_"$tm"

	python3 "$fgs" "$AEType" "$dsType" "$fam1"_"$fam2"_"$fam3" "$sim_cal_id" "$result_dir" "$fp_prefix"_"$fam1.txt" "$fp_prefix"_"$fam2.txt" "$fp_prefix"_"$fam3.txt"

}


# create 1-dimentional feacture vectors for training and testing in detection systems with 2 auxiliary ASRs
1_dim_fv_generation_one_system(){
	fam1=$1
	sim_cal_id=$2

	1_dim_fv_generation_atomic "$fam1"  "$sim_cal_id" "AE" "Train"
	1_dim_fv_generation_atomic "$fam1"  "$sim_cal_id" "Benign" "Train"

	1_dim_fv_generation_atomic "$fam1"  "$sim_cal_id" "AE" "Test"
	1_dim_fv_generation_atomic "$fam1"  "$sim_cal_id" "Benign" "Test"
}

# create 2-dimentional feacture vectors for training and testing in detection systems with 2 auxiliary ASRs
2_dim_fv_generation_one_system(){
	fam1=$1
	fam2=$2
	sim_cal_id=$3

	2_dim_fv_generation_atomic "$fam1" "$fam2" "$sim_cal_id" "AE" "Train"
	2_dim_fv_generation_atomic "$fam1" "$fam2" "$sim_cal_id" "Benign" "Train"

	2_dim_fv_generation_atomic "$fam1" "$fam2" "$sim_cal_id" "AE" "Test"
	2_dim_fv_generation_atomic "$fam1" "$fam2" "$sim_cal_id" "Benign" "Test"
}

# create 3-dimentional feacture vectors for training and testing in detection systems with 3 auxiliary ASRs
3_dim_fv_generation_one_system(){
	fam1=$1
	fam2=$2
	fam3=$3
	sim_cal_id=$4

	3_dim_fv_generation_atomic "$fam1" "$fam2" "$fam3" "$sim_cal_id" "AE" "Train"
	3_dim_fv_generation_atomic "$fam1" "$fam2" "$fam3" "$sim_cal_id" "Benign" "Train"

	3_dim_fv_generation_atomic "$fam1" "$fam2" "$fam3" "$sim_cal_id" "AE" "Test"
	3_dim_fv_generation_atomic "$fam1" "$fam2" "$fam3" "$sim_cal_id" "Benign" "Test"
}


# create feacture vectors for all 4 kinds detection systems by using one similarity metric
feature_generation() {
	sim_cal_id=$1
	echo "generating feature vectors calculated by $sim_cal_id"

	echo "Processing the case with single aux models: $am1"
	1_dim_fv_generation_one_system "$am1" "$sim_cal_id"
	echo "Processing the case with single aux models: $am2"
	1_dim_fv_generation_one_system "$am2" "$sim_cal_id"
	echo "Processing the case with single aux models: $am3"
	1_dim_fv_generation_one_system "$am3" "$sim_cal_id"
	echo "Processing the case with two aux models: $am1 and $am2"
	2_dim_fv_generation_one_system "$am1" "$am2" "$sim_cal_id"
	echo "Processing the case with two aux models: $am1 and $am3"
	2_dim_fv_generation_one_system "$am1" "$am3" "$sim_cal_id"
	echo "Processing the case with two aux models: $am2 and $am3"
	2_dim_fv_generation_one_system "$am2" "$am3" "$sim_cal_id"
	echo "Processing the case with threee aux models: $am1 and $am2 and $am3"
	3_dim_fv_generation_one_system "$am1" "$am2" "$am3" "$sim_cal_id"

	echo "feature generation finished"
}


# generate all 2-aux-models and 3-aux-models feature vectors using 6 similarity metrics one by one
for sim_cal_id in ${sim_cal_ids[*]}
do
	feature_generation "$sim_cal_id"
done

# copy all files of feature vectors into one directory, feature_vectors, inside the result directory
echo "Creating $fv_dir and coping all files of feature vectors into $fv_dir"
rm -rf "$fv_dir" # remove it if it already exists
mkdir "$fv_dir"
for sample_tag in ${sample_tags[*]}
do
	cp "$working_dir"/"$fv_dir_pre""$sample_tag"/* "$fv_dir"
done
echo "Copyi3ng is done!"
