import os.path
import sys
import collections
import getopt
import jellyfish
import matplotlib.pyplot as plt
import numpy as np
from numpy import trapz

Debug=False

# 1.01 is used to create a point when FPR is 1.0
ThresholdRanges=[x/100.0 for x in range(0, 102, 1)]

def phonetic_similarity(ref, result):
	targetTmp = result
	refTmp = ref
	targetTmp = jellyfish.metaphone(result)
	refTmp = jellyfish.metaphone(ref)
	if Debug:
		print ("Result: \t\t" + result)
		print ("Converted result: \t" + targetTmp)
		print ("Ref: \t\t\t" + ref)
		print ("Converted ref: \t\t" + refTmp)
		print ("------------------------------------------------------------------------------")
	return round(jellyfish.jaro_winkler(refTmp, targetTmp), 5)


def loadRefFile(filepath):
	refDict={}
	if Debug:
		print ('Working on ref file: ' + filepath)
	with open(os.path.join(filepath),"rt") as targetFile:
		for line in targetFile:
			parts = line.split()
			refDict[parts[0].strip()] = ' '.join(parts[1:])
	return refDict

# Each line of 'textfile1' and 'textfile2' has the following format:
# 	<filename without file extension> : <recognized transcription>
def similarityScoreCal(textfile1, textfile2):
	dict1=loadRefFile(textfile1)
	scores=[]
	with open(os.path.join(textfile2),"rt") as targetFile:
		for line in targetFile:
			parts = line.split()
			scores.append(phonetic_similarity(dict1[parts[0].strip()],' '.join(parts[1:])))
	return scores

def thresholding(scoresAE, scoresBenign, T):
	totalAEs=len(scoresAE)
	totalBenign=len(scoresBenign)
	TPs, FNs, TNs, FPs=0,0,0,0
	# process scoresAE - TPs and FNs
	for score in scoresAE:
		if score >= T:
			FNs+=1
		else:
			TPs+=1
	# process scoresBenign - TNs and FPs
	for score in scoresBenign:
		if score >= T:
			TNs+=1
		else:
			FPs+=1
	return [TPs, FNs, TNs, FPs]

def training(scoresBenign, givenFPR):
	scoresBenign.sort()
	global ThresholdRanges
	NS=len(scoresBenign)
	curT=ThresholdRanges[0]
	curFPR=0.0
	
	for tempT in ThresholdRanges:
		tempFPs=0
		for score in scoresBenign:
			if score < tempT:
				tempFPs+=1
			else:
				break
		tempFPR=1.0*tempFPs/NS
		if tempFPR <= givenFPR:
			curFPR = tempFPR
			curT = tempT
		else:
			break
	return curT, round(curFPR, 4)

def testing(scoresAE, T):
	scoresAE.sort()
	PS=len(scoresAE)
	TPS=0
	for score in scoresAE:
		if score < T:
			TPS+=1
		else:
			break;
	FNS=PS-TPS
	FNR=1.0*FNS/PS
	return FNS, round(FNR, 4)

def dumpAVector(vec, filePath):
	with open(filePath, "w") as f:
		for item in vec:
			f.write(str(item)+"\n")


def main(argv):
	recogAEFile1=''
	recogAEFile2=''
	recogBenignFile1=''
	recogBenignFile2=''
	if len(argv) != 8:
		print("\n========================================================================================================================")
		print("\nUsage: python <this_script> targetModelTag auxModelTag recogAEFile1 recogAEFile2 recogCleanFile1 recogCleanFile2 resultDir givenFPR")
		print("\n========================================================================================================================")
		return

	targetModelTag = argv[0].strip()
	auxModelTag = argv[1].strip()
	recogAEFile1 = argv[2].strip() 
	recogAEFile2 = argv[3].strip() 
	recogBenignFile1 = argv[4].strip() 
	recogBenignFile2 = argv[5].strip()
	resultDir = argv[6].strip()
	givenFPR = float(argv[7].strip())

	detectorsTag = targetModelTag+"+"+auxModelTag 

	if not os.path.exists(resultDir):
		os.makedirs(resultDir)

	scoresAE=similarityScoreCal(recogAEFile1,recogAEFile2)
	scoresBenign=similarityScoreCal(recogBenignFile1,recogBenignFile2)
	
	scoresBenignFilePath=os.path.join(resultDir,"Scores_of_Benign_Samples_"+detectorsTag+".txt")
	scoresAEFilePath=os.path.join(resultDir,"Scores_of_AE_Samples_"+detectorsTag+".txt")
	dumpAVector(scoresBenign, scoresBenignFilePath)
	dumpAVector(scoresAE, scoresAEFilePath)

	summaryFile=open(os.path.join(resultDir,"summary_"+detectorsTag+".txt"), "w")
	summaryFile.write("givenFPR, Threshold, FPR, FNS, FNR, TPR\n")

	T, FPR = training(scoresBenign, givenFPR)

	FNS, FNR = testing(scoresAE, T)	

	summaryFile.write(str(givenFPR)+", "+str(T)+", "+str(FPR)+", "+str(FNS)+", "+str(FNR)+", "+str(round(1-FNR,4))+"\n")

	summaryFile.close()
main(sys.argv[1:])
