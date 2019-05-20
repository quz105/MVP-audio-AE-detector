# Function:
#	 Part 1:
#	 	Build 7 detection systems. Each of them is built upon one kind of AE together with real bening samples.
#	 	And then test the detection system against unused types (excluding comprehensive type) of AEs.
#	 Part 2:
#		Build the 8th detection system using a comprehensive type of AEs and the number of hypothetically
#		generated benign samples. The comprehensive type of AEs is an assembly of three types of AEs,
#		which are "MME_AE_DS0_DS1_AT", "MME_AE_DS0_DS1_GCS" and  "MME_AE_DS0_GCS_AT".
#
# Input:	the first parameter is result_dir, which holds the building and testing results of each detection system.
#			the second parameter is feature_vectors_dir, which contains all necessary feature-vectors files.
#			feature-vector filenames of AEs are as follows:
#				real AEs			:	"fv_SME_AE_DS0"
#				2-ASRs-effective AEs: 	"fv_MME_AE_DS0_AT",  "fv_MME_AE_DS0_DS1", "fv_MME_AE_DS0_GCS"
#				3-ASRs-effective AEs: 	"fv_MME_AE_DS0_DS1_AT", "fv_MME_AE_DS0_DS1_GCS",  "fv_MME_AE_DS0_GCS_AT"
#				Comprehensive AEs	: 	"fv_Comprehensive_AE" (an assembly of feature vectors of all 3-ASRs-effective AEs)
#			feature-vector filenames of benign samples are as follows:
#				real bening samples	: 	"fv_Real_BS_<num_of_benign_samples>"
#				Comprehensive BSs	:	"fv_Comprehensive_BS_<3 X num_of_benign_samples>"
#
# Output:	as described in "Function", 8 detection systems will be built and tested. For each detecion system,
#			a fold named with the corresponding AEs' type will be created inside "result_dir", in which all the result
#			of building the detection system and testing it over unused types of AEs will be recorded.
#			8 AE_types:
#				real AEs			:	"SME_AE_DS0"
#				2-ASRs-effective AEs:	"MME_AE_DS0_AT",  "MME_AE_DS0_DS1", "MME_AE_DS0_GCS"
#				3-ASRs-effective AEs:	"MME_AE_DS0_DS1_AT", "MME_AE_DS0_DS1_GCS",  "MME_AE_DS0_GCS_AT"
#				Comprehensive AEs   :   "Comprehensive_AE" (an assembly of all 3-ASRs-effective AEs)

import os.path
import sys
import collections
import getopt
import re
import math 
import numpy as np
import random
import shutil

from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

import pickle


def load(filePath):
	fileIDs=[]
	features=[]
	labels=[]
	with open(os.path.join(filePath),"rt") as targetFile:
		lines=targetFile.readlines()
		random.shuffle(lines) # this random shuffling will cause a re-run of model training with the same data to result into a different model because data ordering is changed
		for line in lines:
			parts = line.split(":")
			fileIDs.append(parts[0].strip())
			labels.append(int(parts[2].strip()))
			scores=parts[1].strip().split(",")
			feature=[]
			for score in scores:
				feature.append(round(float(score),4))

			features.append(feature)
		data={}
		data['fileIDs']=fileIDs
		data['features']=features
		data['labels']=labels
	return data

def featurevectorToStr(scores):
	result=""
	dim=len(scores)
	if dim == 0:
		return result;
	result=str(scores[0])
	for i in range(1, dim):
		result+=","+str(scores[i])
	return result;

def predict(classifier, \
			test_fileIDs, test_features, test_labels, \
			falseCaseFilePath):
	# Testing / Inference
	predictedResult=classifier.predict(test_features)
	CPs=0 # # of correct prediction
	EPs=0 # # of errorneous prediction
	numofsamples = len(predictedResult)
	for i in range(0, numofsamples):
		if predictedResult[i] == test_labels[i]:
			CPs+=1
		else:
			EPs+=1
			with open(falseCaseFilePath, "a+") as ff:
				ff.write(test_fileIDs[i]+":"+featurevectorToStr(test_features[i])+"\n")
	return CPs, EPs
		


def predictOnTestset(classifier, \
					testAE_fileIDs, testAE_features, testAE_labels, \
					testBenign_fileIDs, testBenign_features, testBenign_labels, \
					falseNegFilePath, falsePosFilePath, resultFile):
	# Testing / Inference
	TPs, FNs = predict(	classifier, \
						testAE_fileIDs, testAE_features, testAE_labels, \
						falseNegFilePath)

	TNs, FPs = predict( classifier, \
						testBenign_fileIDs, testBenign_features, testBenign_labels, \
						falsePosFilePath)

	with open(resultFile, "w") as rf:
		accuracy=round(1.0*(TPs+TNs)/(TPs+TNs+FNs+FPs), 4)
		FPR = round(1.0*FPs/(TNs+FPs), 4)
		FNR = round(1.0*FNs/(TPs+FNs), 4)
		rf.write("Accuracy: "+str(accuracy)+", FPR: "+str(FPR)+", FNR: "+str(FNR)+", FNs: "+str(FNs)+", FPs: "+str(FPs)+"\n")
		#rf.write("[Debug] TPs:"+str(TPs)+", FNs:"+str(FNs)+", TNs:"+str(TNs)+", FPs:"+str(FPs)+"\n")
#

def batchdataload(fv_names, feature_vectors_dir):
	fv_data={}
	for fv_name in fv_names:
		data = load(os.path.join(feature_vectors_dir, fv_name))
		fv_data[fv_name[3:]]=data # fv_name has the format "fv_<AE type>". So, use fv_name[3:] to retrieve the AE's type 
	return fv_data

def prepareTrainandTestData(data, ratio_of_training_part):
	num_of_training_samples=int(len(data['features'])*ratio_of_training_part)
	print("[prepareTrainedTestData] len(data): {}, ratio_of_training_part: {}, and num_of_training_samples: {}.".
		format(len(data), ratio_of_training_part, num_of_training_samples))
	train_data={}
	test_data={}
	for key in data:
		train_data[key]=[]
		test_data[key]=[]
		for idx in range(len(data[key])):
			if idx < num_of_training_samples:
				train_data[key].append(data[key][idx])
			else:
				test_data[key].append(data[key][idx])
	return train_data, test_data

def predictOnUnUsedAE(classifier, \
					AE_fileIDs, AE_features, AE_labels, \
					falseNegFilePath, resultFile):
	TPs, FNs = predict(	classifier, \
						AE_fileIDs, AE_features, AE_labels, \
						falseNegFilePath)
	with open(resultFile, "w") as rf:
		TPR=round(1.0*(TPs)/(TPs+FNs), 4)
		FNR = round(1.0*FNs/(TPs+FNs), 4)
		rf.write("[Unused AEs] TPR: "+str(TPR)+", TPs: "+str(TPs)+", FNR: "+str(FNR)+", FNs: "+str(FNs)+"\n")
#


def main(argv):
	if len(argv) != 2:
		print("\n==========================================================")
		print("\nUsage: python <this_script> result_dir feature_vectors_dir")
		print("\n==========================================================")
		return

	# Parameters Configuration
	result_dir=sys.argv[1]
	feature_vectors_dir=sys.argv[2]

	
	num_of_real_Benign_Samples=2400
	fv_real_BS_filename="fv_Real_BS_"+str(num_of_real_Benign_Samples)
	fv_comprehensive_BS_filename="fv_Comprehensive_BS_"+str(3*num_of_real_Benign_Samples)

	fv_AE_names=[	"fv_SME_AE_DS0",
					"fv_MME_AE_DS0_AT",  "fv_MME_AE_DS0_DS1", "fv_MME_AE_DS0_GCS",
					"fv_MME_AE_DS0_DS1_AT", "fv_MME_AE_DS0_DS1_GCS",  "fv_MME_AE_DS0_GCS_AT",
					"fv_Comprehensive_AE"]

	AE_types=[	"SME_AE_DS0",
				"MME_AE_DS0_AT",  "MME_AE_DS0_DS1", "MME_AE_DS0_GCS",
				"MME_AE_DS0_DS1_AT", "MME_AE_DS0_DS1_GCS",  "MME_AE_DS0_GCS_AT"]

	# Data load
	fv_AE_data=batchdataload(fv_AE_names, feature_vectors_dir)
	fv_Real_BS_data=load(os.path.join(feature_vectors_dir,fv_real_BS_filename))
	fv_Comprehensive_BS_data=load(os.path.join(feature_vectors_dir,fv_comprehensive_BS_filename))

	# Build 8 detection systems and have them tested.
	ratio_of_training_part=0.8
	for AE_type in fv_AE_data:
		print("Experiment with AE type: "+AE_type)

		# Prepare Training and Testing sets
		train_data_AE, test_data_AE=prepareTrainandTestData(fv_AE_data[AE_type], ratio_of_training_part)
		fv_BS_data=fv_Real_BS_data
		if AE_type == "Comprehensive_AE":
			fv_BS_data=fv_Comprehensive_BS_data
		train_data_BS, test_data_BS=prepareTrainandTestData(fv_BS_data, ratio_of_training_part)	

		resultDir=os.path.join(result_dir,AE_type)
		shutil.rmtree(resultDir, ignore_errors=True)
		os.makedirs(resultDir)

		trainFeatures=train_data_AE['features']
		trainFeatures.extend(train_data_BS['features'])
		trainLabels=train_data_AE['labels']
		trainLabels.extend(train_data_BS['labels'])

		# Training
		print("Trainging is started")
		clf=SVC(kernel='poly', degree=3, tol=1e-4, gamma='auto')
		clf.fit(trainFeatures, trainLabels)
		print("Traing is done!")

		# Validation: Test trained model against testset
		falseNegFilePath=os.path.join(resultDir, AE_type+"_falseNegativeCases.txt")
		falsePosFilePath=os.path.join(resultDir, AE_type+"_falsePositiveCases.txt")

		resultFile=os.path.join(resultDir, "result_"+AE_type+".txt")
		print("Prediction on Test set: "+falseNegFilePath+", "+falsePosFilePath+", "+resultFile)

		predictOnTestset(	clf, \
							test_data_AE['fileIDs'], test_data_AE['features'], test_data_AE['labels'], \
							test_data_BS['fileIDs'], test_data_BS['features'], test_data_BS['labels'], \
							falseNegFilePath, falsePosFilePath, resultFile)

		print("Prediction on Test set: Done!")


		# Testing with unused types of AEs
		unused_AE_types=[]
		if AE_type == "Comprehensive_AE":
			unused_AE_types=AE_types[0:4] # "SME_AE_DS0", "MME_AE_DS0_AT",  "MME_AE_DS0_DS1" and "MME_AE_DS0_GCS"
		else:
			for test_AE_type in AE_types:
				if test_AE_type!=AE_type:
					unused_AE_types.append(test_AE_type)

		for test_AE_type in unused_AE_types:
			print("Testing with unused AE: "+ test_AE_type)
			falseNegFilePath_unusedAE=os.path.join(resultDir, "testing_unusedAE_"+test_AE_type+"_falseNegativeCases.txt")
			resultFile_unusedAE=os.path.join(resultDir, "result_testing_unusedAE_"+test_AE_type+".txt")
			predictOnUnUsedAE(clf, \
					fv_AE_data[test_AE_type]['fileIDs'], fv_AE_data[test_AE_type]['features'], fv_AE_data[test_AE_type]['labels'], \
					falseNegFilePath_unusedAE, resultFile_unusedAE)

		# save the trained model
		pickle.dump(clf, open(os.path.join(resultDir, "svm_model_"+AE_type+".sav"), 'wb'))


main(sys.argv[1:])
