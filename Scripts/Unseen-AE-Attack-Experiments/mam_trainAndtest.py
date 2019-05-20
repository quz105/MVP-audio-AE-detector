import os.path
import sys
import collections
import getopt
import re
import math 
import numpy as np

from sklearn.svm import SVC

Debug=False
	
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


def prediction_on_AEs(	classifier, \
				testAE_fileIDs, testAE_features, testAE_labels, \
				falseNegFilePath, resultFile):
	# Testing / Inference
	predictedResult_AESamples=classifier.predict(testAE_features)
	TPs=0
	FNs=0
	numofAEs = len(predictedResult_AESamples)
	for i in range(0, numofAEs):
		if predictedResult_AESamples[i] == testAE_labels[i]:
			TPs+=1
		else:
			FNs+=1
			print("\t[FNs]: "+str(FNs)+", "+testAE_fileIDs[i]+":"+featurevectorToStr(testAE_features[i]))
			with open(falseNegFilePath, "a+") as fn:
				fn.write(testAE_fileIDs[i]+":"+featurevectorToStr(testAE_features[i])+"\n")

	with open(resultFile, "w+") as rf:
		FNR = round(1.0*FNs/(TPs+FNs), 4)
		TPR = 1-FNR
		rf.write("FNR: "+str(FNR)+", FNs: "+str(FNs)+", TPR: "+str(TPR)+"\n")
		print("\t[FNR]: "+str(FNR)+", FNs: "+str(FNs)+", TPR: "+str(TPR)+"\n")

#

def main(argv):
	if len(argv) != 6:
		print("\n======================================================================================================================================")
		print("\n==========Usage: python <this_script> AETrainDataFile BenignTrainDataFile AuxModelsTag SimCalID AEUNKDataFile ResultDir===============")
		print("\n======================================================================================================================================")
		return

	print("\tStarting training")
	AETrainPath = argv[0].strip()
	BenignTrainPath = argv[1].strip()
	Aux_Models_Tag=argv[2].strip()
	SimCalID=argv[3].strip()
	AEUnseenPath=argv[4].strip()
	ResultDir=argv[5].strip()

	if Debug:
		print("\t"+AETrainPath+"\n\t"+BenignTrainPath+"\n\t"+Aux_Models_Tag+"\n\t"+SimCalID+"\n\t"+AEUnseenPath)

	trainAE_fileIDs, trainAE_features, trainAE_labels = load(AETrainPath)	

	trainBenign_fileIDs, trainBenign_features, trainBenign_labels = load(BenignTrainPath)

	unseenAE_fileIDs, unseenAE_features, unseenAE_labels = load(AEUnseenPath)



	# Training
	trainFeatures=trainAE_features
	trainFeatures.extend(trainBenign_features)
	trainLabels=trainAE_labels
	trainLabels.extend(trainBenign_labels)

	# use SVM as the binary classifier
	#	1.	For experimental results presented AAAI workshop paper, the default value of gamma was used, which is 'auto'.
	# 	2.	For experimental results presented in DSN paper (submitted), the value of gamma was set to 'scale' to remove.
	#		a future warning from sklearn Python package. It is said that, starting version 0.22, the default value of
	#		gamma will be changed to 'scale'.
	clf=SVC(kernel='poly', degree=3, tol=1e-4, gamma='scale')
	clf.fit(trainFeatures, trainLabels)

	# Test trained model against unseen AEs
	falseNegFilePath=os.path.join(ResultDir, "UnseenAE_falseNegativeCases_"+SimCalID+"_"+Aux_Models_Tag+".txt")
	resultFile=os.path.join(ResultDir, "UnseenAE_result_"+SimCalID+"_"+Aux_Models_Tag+".txt")
	print("\tDetecting a set of unseen AEs: \n\t"+falseNegFilePath+"\n\t"+resultFile)

	prediction_on_AEs(	clf, \
				unseenAE_fileIDs, unseenAE_features, unseenAE_labels, \
				falseNegFilePath, resultFile)

	print("\tDetecting a set of unseen AEs: Done!\n")



main(sys.argv[1:])
