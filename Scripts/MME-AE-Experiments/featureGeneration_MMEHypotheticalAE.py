# Function:	create feature vectors for
#			(1) 6 types of hypothetical multiple-ASRs-effective AEs,
#			(2) comprehensive type of AEs,
#			(3) the same number (as that of the comprehensive AEs) of hypothetical benign samples
#
# Input:	the first parameter is actural_scores_dir where there are six similarity-scores files,
#			AE_AT.txt, AE_DS1.txt, AE_GCS.txt, Benign_AT.txt, Benign_DS1.txt and Benign_GCS.txt.
#			Each of them contains similarity scores of each audio's transcriptions recognized by DS0
#			and another ASR indicated by the filename. The type of audios is indicated in the filename,
#			either "AE" (Adversarial Example) or "Benign" (Benign Sample).
#
# Output:	generate 8 feature-vectors files inside "actural_scores_dir", as described in “Function”.

import os.path
import sys
import collections
import getopt
import re
import math 
import numpy as np
import random

from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

#AE_raw_scores=[] # DS1, GCS, AT
#AE_fileIDs=[]
#BS_raw_scores=[] # DS1, GCS, AT
#BS_fileIDs=[]
	
def load(filePath):
	fileIDs=[]
	features=[]
	labels=[]
	with open(os.path.join(filePath),"rt") as targetFile:
		for line in targetFile:
			parts = line.split(":")
			fileIDs.append(parts[0].strip())
			labels.append(int(parts[2].strip()))
			scores=parts[1].strip().split(",")
			feature=[]
			for score in scores:
				feature.append(round(float(score),4))
			features.append(feature)
	return fileIDs, features, labels

def featurevectorToStr(scores):
	result=""
	dim=len(scores)
	if dim == 0:
		return result;
	result=str(scores[0])
	for i in range(1, dim):
		result+=","+str(scores[i])
	return result;


def loadScores(filepath):
	scores=[]
	fileIDs=[]
	with open(filepath, "r") as sf:
		for line in sf.readlines():
			line=line.strip()
			parts=line.split(":")
			fileIDs.append(parts[0])
			scores.append(round(float(parts[1]), 4))
	return scores, fileIDs

def main(argv):
	if len(argv) != 1:
		print("\n==============================================")
		print("\nUsage: python <this_script> actural_scores_dir")
		print("\n==============================================")
		return

	actural_scores_dir=sys.argv[1].strip()
#	global AE_raw_scores
#	global BS_raw_scores
#	global AE_fileIDs
#	global BS_fileIDs
	AE_raw_scores=[] # DS1, GCS, AT
	AE_fileIDs=[]
	BS_raw_scores=[] # DS1, GCS, AT
	BS_fileIDs=[]
	
	
	# inside "actural_scores_dir", there should have six similarity-score files
	# named as "AE_DS1.txt", "AE_GCS.txt", "AE_AT.txt", "Benign_DS1.txt",
	# "Benign_GCS.txt" and "Benign_AT.txt".
	AEscorefilenamelist=["AE_DS1.txt", "AE_GCS.txt", "AE_AT.txt"]
	BSscorefilenamelist=["Benign_DS1.txt", "Benign_GCS.txt", "Benign_AT.txt"]

	for filename in AEscorefilenamelist:
		scores, fileIDs = loadScores(os.path.join(actural_scores_dir, filename))
		AE_raw_scores.append(scores)
		AE_fileIDs.append(fileIDs)

	for filename in BSscorefilenamelist:
		scores, fileIDs = loadScores(os.path.join(actural_scores_dir, filename))
		BS_raw_scores.append(scores)
		BS_fileIDs.append(fileIDs)

	numOfAEsToCreate=2400#1125
	numOfActuralAEs=2400#1125
	numOfActuralBSs=2400#1125


	print("start to generate hypothetical MME AEs")
	filePrefix="fv_MME_AE"
	# 1: use distribution of benign samples to obtain hypotheical score
	# 0: use distribution of adversarial samples to obtain hypotheical score
	fileTags={	"DS0_DS1":[1,0,0],\
				"DS0_GCS":[0,1,0],\
				"DS0_AT" :[0,0,1],\
				"DS0_DS1_GCS":[1,1,0],\
				"DS0_DS1_AT" :[1,0,1],\
				"DS0_GCS_AT" :[0,1,1]\
				}

	for tag in fileTags:
		print("creating MME AEs:"+tag)
		feature_vector_filepath=os.path.join(actural_scores_dir, filePrefix+"_"+tag)
		feature_vector_fileIDs_filepath=os.path.join(actural_scores_dir, filePrefix+"_"+tag+"_fileIDs")
		labels=fileTags[tag]
		scores=np.zeros(len(labels))
		fileIDs=['']*len(labels)
		with open(feature_vector_filepath, "w+") as fvf, open(feature_vector_fileIDs_filepath, "w+") as fvff:
			for idx in range(0,numOfAEsToCreate):
				for i in range(0,len(labels)):
					rnd_idx=random.randrange(numOfActuralAEs)
					if labels[i] == 1:
						scores[i]=BS_raw_scores[i][rnd_idx]
						fileIDs[i]=BS_fileIDs[i][rnd_idx]
					else:
						scores[i]=AE_raw_scores[i][rnd_idx]
						fileIDs[i]=AE_fileIDs[i][rnd_idx]
				fvf.write(tag+"_"+str(idx+1)+":"+featurevectorToStr(scores)+":1\n") # the ending digit 1 indicates this sample is an AE

				fvff.write(tag+"_"+str(idx+1)+":") 
				for fileID in fileIDs:
					fvff.write(fileID+",")
				fvff.write("\n")
 
	# generate (3 X numOfAEsToCreate) feature vectors of Benign samples.
	# They will be grouped with 3ME_DS1_GCS, 3ME_DS1_AT and 3ME_AT AEs
	# to train and test a powerful detection system.
	groupsOf3ME_AE=3
	numOfSelectedBSs=groupsOf3ME_AE*numOfAEsToCreate
	print("creating " + str(numOfSelectedBSs) + " 3-dimensional feature vectors for benign samples")
	benign_sample_filename="fv_Comprehensive_BS_"+str(numOfSelectedBSs)
	benign_sample_filepath=os.path.join(actural_scores_dir, benign_sample_filename)
	benign_sample_fileID_filepath=os.path.join(actural_scores_dir, benign_sample_filename+"_fileIDs")
	scores=np.zeros(groupsOf3ME_AE)
	with open(benign_sample_filepath, "w+") as bsf, open(benign_sample_fileID_filepath, "w+") as bsff:
		for idx in range(0, numOfSelectedBSs):
			bsff.write("BS_"+str(idx+1)+":")
			for i in range(0,len(scores)):
				bsff.write(BS_fileIDs[i][rnd_idx]+",")
				rnd_idx=random.randrange(numOfActuralBSs)
				scores[i]=BS_raw_scores[i][rnd_idx]
			bsff.write("\n")
			bsf.write("BS_"+str(idx+1)+":"+featurevectorToStr(scores)+":0\n") # the ending digit 0 indicates this sample is a benign sample


	# group feature vectors of 3ME_DS1_GCS, 3ME_DS1_AT and 3ME_AT AEs to
	# a comprehensive type of AEs. The total number of AEs is 3XnumOfActuralAEs(7200).
	print("creating "+str(3*numOfActuralAEs)+" comprehensive type of AEs!")
	comprehensive_AEs_filename="fv_Comprehensive_AE"
	comprehensive_AEs_filepath=os.path.join(actural_scores_dir, comprehensive_AEs_filename)
	comprehensive_AEs_fileID_filepath=os.path.join(actural_scores_dir, comprehensive_AEs_filename+"_fileIDs")
	types_of_comprehensive_AEs=["DS0_DS1_GCS", "DS0_DS1_AT", "DS0_GCS_AT"]
	feature_vectors_comprehensive_AEs=[]
	fileIDs_info=[]
	for tag in fileTags:
		if tag in types_of_comprehensive_AEs:
			feature_vector_filepath=os.path.join(actural_scores_dir, filePrefix+"_"+tag)
			feature_vector_fileIDs_filepath=os.path.join(actural_scores_dir, filePrefix+"_"+tag+"_fileIDs")
			with open(feature_vector_filepath) as fvf, open(feature_vector_fileIDs_filepath) as fvff:
				feature_vector_lines=fvf.readlines()
				fileIDs_lines=fvff.readlines()	
				feature_vectors_comprehensive_AEs.extend(feature_vector_lines)
				fileIDs_info.extend(fileIDs_lines)

	with open(comprehensive_AEs_filepath, "w") as cAEf, open(comprehensive_AEs_fileID_filepath, "w") as cAEff:
		random.shuffle(feature_vectors_comprehensive_AEs)
		for line in feature_vectors_comprehensive_AEs:
			cAEf.write(line)
		for line in fileIDs_info:
			cAEff.write(line)

main(sys.argv[1:])
