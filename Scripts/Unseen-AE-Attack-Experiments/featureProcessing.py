import os.path
import sys
import collections
import getopt
import re

from sklearn.neighbors import KNeighborsClassifier


def featureVectorProcessing(scoreFilesPaths, isAE, datasetType, aux_models_tag, sim_cal_id, resultDir):
	scoreObjs=[]
	for sf in scoreFilesPaths:
		scores={}
		with open(os.path.join(sf),"rt") as targetFile:
			for line in targetFile:
				parts = line.split(":")
				scores[parts[0].strip()]=float(" ".join(parts[1:]))
		scoreObjs.append(scores)
	label=0
	if isAE == "Yes":
		label=1

	features_IDs={}
	for key in scoreObjs[0]:
		features_IDs[key]=[]

	fileIDs=[]
	features=[]
	labels=[]
	for key in features_IDs:
		fileIDs.append(key)
		labels.append(label)
		feature=[]
		for scores in scoreObjs:
			feature.append(scores[key])
		features.append(feature)

	resultfilepath="feature_vectors_"+sim_cal_id
	if isAE == "Yes":
		resultfilepath+="_AE"
	else:
		resultfilepath+="_Benign"

	if datasetType == "Test":
		resultfilepath+="_Test"
	elif datasetType == "Train":
		resultfilepath+="_Train"
	elif datasetType == "Unseen":
		resultfilepath+="_Unseen"
	resultfilepath+="_"+aux_models_tag+".txt"
	resultfilepath=os.path.join(resultDir, resultfilepath)

	with open(resultfilepath, "w") as fv:
		length=len(fileIDs)
		for x in range(0,length):
			fs=str(round(features[x][0], 4))
			dim=len(features[x])
			for i in range(1, dim):
				fs+=","+str(round(features[x][i], 4))
			fv.write(fileIDs[x]+":"+fs+":"+str(labels[x])+"\n")
		

def main(argv):
	if (len(argv) < 6):
		print("\n===============================================================================================")
		print("\nUsage: python <this_script> resultDir isAE datasetType aux_models_tag sim_cal_id list_of_filepaths" )
		print("\n===============================================================================================")
		return

	resultDir = argv[0].strip()
	isAE = argv[1].strip()
	datasetType = argv[2].strip()
	aux_models_tag = argv[3].strip()
	sim_cal_id=argv[4].strip()
	listoffilepaths=argv[5:]
	

	featureVectorProcessing(listoffilepaths, isAE, datasetType, aux_models_tag, sim_cal_id, resultDir)

main(sys.argv[1:])
