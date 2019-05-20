#/bin/bash


# Function:
#	 Part 1:
#	 	Build 7 detection systems. Each of them is built upon one kind of AE together with real bening samples.
#	 	And then test the detection system against unused types (excluding comprehensive type) of AEs.
#	 Part 2:
#		Build the 8th detection system using a comprehensive type of AEs and the number of hypothetically
#		generated benign samples. The comprehensive type of AEs is an assembly of three types of AEs,
#		which are "MME_AE_DS0_DS1_AT", "MME_AE_DS0_DS1_GCS" and  "MME_AE_DS0_GCS_AT".
#
# Input:	The first parameter is RESULT_DIR, which holds the building and testing results of each detection system.
#			The second parameter is SS_FV_DIR, which contains all necessary similarity-score files and feature-vectors files.
#				Six prepared similarity-score files are:
#					AE_AT.txt, AE_DS1.txt, AE_GCS.txt, Benign_AT.txt, Benign_DS1.txt and Benign_GCS.txt.
#					Each of them contains similarity scores of each audio's transcriptions recognized by DS0
#					and another ASR indicated by the filename. The type of audios is indicated in the filename,
#					either "AE" (Adversarial Example) or "Benign" (Benign Sample).
#				Two prepared feature-vector files are:
#					real AEs			:	"fv_SME_AE_DS0"
#					real bening samples	: 	"fv_Real_BS_<num_of_benign_samples>"
#				feature-vector filenames for 7 types of AEs, which will be created by "featureGeneration_MMEHypotheticalAE.py", are:
#					2-ASRs-effective AEs: 	"fv_MME_AE_DS0_AT",  "fv_MME_AE_DS0_DS1", "fv_MME_AE_DS0_GCS"
#					3-ASRs-effective AEs: 	"fv_MME_AE_DS0_DS1_AT", "fv_MME_AE_DS0_DS1_GCS",  "fv_MME_AE_DS0_GCS_AT"
#					Comprehensive AEs	: 	"fv_Comprehensive_AE" (an assembly of feature vectors of all 3-ASRs-effective AEs)
#				feature-vector filename for benign samples, which will be created by "featureGeneration_MMEHypotheticalAE.py", is:
#					Comprehensive BSs	:	"fv_Comprehensive_BS_<3 X num_of_benign_samples>"
#
# Output:	As described in "Function", 8 detection systems will be built and tested. For each detection system,
#			a fold named with the corresponding AEs' type will be created inside "RESULT_DIR", in which all the result
#			of building the detection system and testing it over unused types of AEs will be recorded.
#			8 AE_types:
#				real AEs			:	"SME_AE_DS0"
#				2-ASRs-effective AEs:	"MME_AE_DS0_AT",  "MME_AE_DS0_DS1", "MME_AE_DS0_GCS"
#				3-ASRs-effective AEs:	"MME_AE_DS0_DS1_AT", "MME_AE_DS0_DS1_GCS",  "MME_AE_DS0_GCS_AT"
#				Comprehensive AEs   :   "Comprehensive_AE" (an assembly of all 3-ASRs-effective AEs)


RESULT_DIR=$1
SS_FV_DIR=$2 # directory that holds similarity scores and feature vectors


single_run(){
	result_dir=$1
	ss_fv_dir=$2

	echo -e "\n[Creating feature vectors for multiple-ASRs-effective AEs]"
	python featureGeneration_MMEHypotheticalAE.py "$SS_FV_DIR"

	echo -e "\n[Building 8 detection systems and test them on unused types of AEs]"
	python buildAndtest.py "$RESULT_DIR" "$SS_FV_DIR"
}

single_run "$RESULT_DIR" "$SS_FV_DIR"
