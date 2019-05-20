import os.path
import sys
import collections
import getopt
import re
import math 
import numpy as np

from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import pickle

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

	with open(resultFile, "a+") as rf:
		accuracy=round(1.0*(TPs+TNs)/(TPs+TNs+FNs+FPs), 4)
		FPR = round(1.0*FPs/(TNs+FPs), 4)
		FNR = round(1.0*FNs/(TPs+FNs), 4)
		rf.write("Accuracy: "+str(accuracy)+", FPR: "+str(FPR)+", FNR: "+str(FNR)+", FNs: "+str(FNs)+", FPs: "+str(FPs)+"\n")

	Accuracy=round(1.0*(TPs+TNs)/(TPs+FPs+TNs+FNs), 4)
	result={"TPs":[], "FNs":[], "TNs":[], "FPs":[], "FNR":[], "FPR":[], "Accuracy":[]}
	result["TPs"].append(TPs)
	result["FNs"].append(FNs)
	result["TNs"].append(TNs)
	result["FPs"].append(FPs)
	result["FNR"].append(FNR)           
	result["FPR"].append(FPR)
	result["Accuracy"].append(Accuracy)

	return result
#


def trainAndtest(
	AETrainPath,
	BenignTrainPath,
	AETestPath,
	BenignTestPath,
	Classifier,
	Aux_Models_Tag,
	SimCalID,
	resultDir,
        modelFilepath):

	print("\t[Starting training]")

	print("\t\t"+AETrainPath+"\n\t\t"+BenignTrainPath+"\n\t\t"+AETestPath+"\n\t\t"+BenignTestPath+"\n\t\t"+Classifier+"\n\t\t"+Aux_Models_Tag+"\n\t\t"+SimCalID)

	trainAE_fileIDs, trainAE_features, trainAE_labels = load(AETrainPath)	

	trainBenign_fileIDs, trainBenign_features, trainBenign_labels = load(BenignTrainPath)

	testAE_fileIDs, testAE_features, testAE_labels = load(AETestPath)

	testBenign_fileIDs, testBenign_features, testBenign_labels = load(BenignTestPath)

	if not os.path.exists(resultDir):
		os.makedirs(resultDir)


	# Training
	trainFeatures=trainAE_features
	trainFeatures.extend(trainBenign_features)
	trainLabels=trainAE_labels
	trainLabels.extend(trainBenign_labels)

	clf=None
	if Classifier == "SVM":
		#	1.	For experimental results presented AAAI workshop paper, the default value of gamma was used, which is 'auto'.
		# 	2.	For experimental results presented in DSN paper (submitted), the value of gamma was set to 'scale' to remove.
		#		a future warning from sklearn Python package. It is said that starting version 0.22, the default value of
		#		gamma will be changed to 'scale'.
		clf=SVC(kernel='poly', degree=3, tol=1e-4, gamma='scale')
	elif Classifier == "KNN":
		clf = KNeighborsClassifier(n_neighbors=10, weights='distance')
	elif Classifier == "RandomForest":
		clf=RandomForestClassifier(random_state=200)
	else:
		raise Exception("Unsupported Binary Classifier "+Classifier)
	clf.fit(trainFeatures, trainLabels)

	pickle.dump(clf, open(modelFilepath, 'wb'))
	print("\t[Traing is Done]")

	# Testing / Inference
	# Test trained model against testset
	falseNegFilePath=os.path.join(resultDir, "falseNegativeCases_"+SimCalID+"_"+Aux_Models_Tag+"_"+Classifier+".txt")
	falsePosFilePath=os.path.join(resultDir, "falsePositiveCases_"+SimCalID+"_"+Aux_Models_Tag+"_"+Classifier+".txt")
	
	resultFile=os.path.join(resultDir, "result_"+SimCalID+"_"+Aux_Models_Tag+"_"+Classifier+".txt")
	print("\n\t[Prediction on Test set]\n\t\t"+falseNegFilePath+"\n\t\t"+falsePosFilePath+"\n\t\t"+resultFile)

	result=predictOnTestset(clf, \
						testAE_fileIDs, testAE_features, testAE_labels, \
						testBenign_fileIDs, testBenign_features, testBenign_labels, \
						falseNegFilePath, falsePosFilePath, resultFile)

	print("\t[Prediction on Test set: Done!]")
	return result
