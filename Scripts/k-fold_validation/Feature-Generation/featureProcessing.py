import os.path
import sys
import collections
import getopt
import re

def featureVectorProcessing(scoreFilesPaths, AEType, dsType, aux_models_tag, sim_cal_id, resultDir):
	scoreObjs=[]
	for sf in scoreFilesPaths:
		scores={}
		with open(os.path.join(sf),"rt") as targetFile:
			for line in targetFile:
				parts = line.split(":")
				scores[parts[0].strip()]=float(" ".join(parts[1:]))
		scoreObjs.append(scores)
	
	label=0
	if AEType == "AE":
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

	resultfilepath="feature_vectors_"+sim_cal_id+"_"+AEType+"_"+dsType+"_"+aux_models_tag+".txt"

	with open(os.path.join(resultDir,resultfilepath), "w") as fv:
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
		print("\nUsage: python <this_script> AEType dsType aux_models_tag sim_cal_id result_dir list_of_filepaths" )
		print("\n===============================================================================================")
		return

	AEType = argv[0].strip()
	dsType = argv[1].strip()
	aux_models_tag = argv[2].strip()
	sim_cal_id=argv[3].strip()
	result_dir=argv[4].strip()
	listoffilepaths=argv[5:]

	if not os.path.exists(result_dir):
			os.makedirs(result_dir)



	featureVectorProcessing(listoffilepaths, AEType, dsType, aux_models_tag, sim_cal_id, result_dir)

main(sys.argv[1:])
