import os.path
import sys
import collections
import getopt
import statistics
import jellyfish
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from numpy import trapz

Debug=False
# 1.01 is used to create a point when FPR is 1.0
ThresholdRanges=[x/100.0 for x in range(0, 102, 1)]

def curvePlot2(allTPs,allFNs,allTNs,allFPs, xlabel, ylabel, outputfile, title):
	print("\t[curvePlot2] ploting " + outputfile)
	global ThresholdRanges
	dx=ThresholdRanges
	plt.plot(dx, np.array(allTPs),'--o')
	plt.plot(dx, np.array(allFNs),'--h')
	plt.plot(dx, np.array(allTNs),'--+')
	plt.plot(dx, np.array(allFPs),'--x')
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	plt.legend(["TPs", "FNs", "TNs", "FPs"], loc='lower right')
	plt.savefig(outputfile)
	plt.close()
	print("\tploting finished!")

def curvePlot(xs, ys, xlabel, ylabel, outputfile, linetag, title):
	print("\t[curvePlot] ploting " + outputfile)

	plt.plot(xs, ys,'--o')
	plt.xlabel(xlabel, fontsize=18)
	plt.ylabel(ylabel, fontsize=18)
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)
	#pylab.title(title)
	plt.legend([linetag], loc='lower right', fontsize=18)
	plt.tight_layout()
	#plt.show()
	plt.savefig(outputfile)
	plt.close()
	print("\tploting finished!")

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
	return jellyfish.jaro_winkler(refTmp, targetTmp)


def loadRefFile(filepath):
	refDict={}
	with open(os.path.join(filepath),"rt") as targetFile:
		for line in targetFile:
			parts = line.split()
			refDict[parts[0].strip()] = ' '.join(parts[1:])
	return refDict

# Each line of 'textfile1' and 'textfile2' has the following format:
# 	<filename without file extension> : <recognized transcription> 
def similarityScoreCalTrain(textfile1, textfile2):
	dict1=loadRefFile(textfile1)
	scores=[]
	with open(os.path.join(textfile2),"rt") as targetFile:
		for line in targetFile:
			parts = line.split()
			if Debug:
				print(dict1[parts[0].strip()])
				print(parts[1:])
			scores.append(phonetic_similarity(dict1[parts[0].strip()],' '.join(parts[1:])))
	return scores

def thresholdingTrain(scoresAE, scoresBenign, T):
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


def train(
    targetModelTag,
	auxModelTag,
	datasetsTag,
	recogAEFile1, 
	recogAEFile2, 
	recogBenignFile1, 
	recogBenignFile2,
	resultDir):

	detectorsTag = targetModelTag+"+"+auxModelTag 
	if not os.path.exists(resultDir):
		os.makedirs(resultDir)
	scoresAE=similarityScoreCalTrain(recogAEFile1,recogAEFile2)
	scoresBenign=similarityScoreCalTrain(recogBenignFile1,recogBenignFile2)
	TPRs, FPRs = [], []
	allTPs, allFNs, allTNs, allFPs = [], [], [], []
	optimal_RoC_Point={"T":0,"maxTPPlusTN":0,"TPs":0,"FNs":0,"TNs":0,"FPs":0}

	summaryFile=open(os.path.join(resultDir,"summary_"+detectorsTag+"_"+datasetsTag+".txt"), "w")

	summaryFile.write("Threshold, TPs, FNs, TNs, FPs\n")
	global ThresholdRanges

	for T in ThresholdRanges:
		[TPs,FNs,TNs,FPs]=thresholdingTrain(scoresAE, scoresBenign, T)
		allTPs.append(TPs)
		allFNs.append(FNs)
		allTNs.append(TNs)
		allFPs.append(FPs)
		TPR=round((1.0*TPs)/(TPs+FNs), 4)
		FPR=round((1.0*FPs)/(TNs+FPs), 4)
		TPRs.append(TPR)
		FPRs.append(FPR)
		if optimal_RoC_Point["maxTPPlusTN"] < (TPs+TNs):
			optimal_RoC_Point["maxTPPlusTN"]=TPs+TNs
			optimal_RoC_Point["T"]=T
			optimal_RoC_Point["TPs"]=TPs
			optimal_RoC_Point["FNs"]=FNs
			optimal_RoC_Point["TNs"]=TNs
			optimal_RoC_Point["FPs"]=FPs
		summaryFile.write(str(T)+", "+str(TPs)+", "+str(FNs)+", "+str(TNs)+", "+str(FPs)+"\n")

	optimalTPR_RoC=optimal_RoC_Point["TPs"]/len(scoresAE)
	optimalFPR_RoC=optimal_RoC_Point["FPs"]/len(scoresBenign)
	optimal_RoC_Point["TPR"]=round(optimalTPR_RoC, 4)
	optimal_RoC_Point["FPR"]=round(optimalFPR_RoC, 4)

	AuC=round(trapz(TPRs, FPRs), 4)
	optimal_RoC_Point["AuC"]=AuC
	summaryFile.write("\n\nOptimal RoC Point: "+str(optimal_RoC_Point["maxTPPlusTN"])+"/maxTPPlusTN, "+str(optimal_RoC_Point["T"])+"/T, "+str(optimal_RoC_Point["TPs"])+"/TPs, "+str(optimal_RoC_Point["FNs"])+"/FNs, "+str(optimal_RoC_Point["TNs"])+"/TNs, "+str(optimal_RoC_Point["FPs"])+"/FPs, "+str(optimalTPR_RoC)+"/TPR, "+str(optimalFPR_RoC)+"/FPR, "+str(AuC)+"/AuC\n")


	summaryFile.close()
	modelFilename="model_"+detectorsTag+"_"+str(optimal_RoC_Point["T"])+"_"+datasetsTag+".txt"
	modelFilepath=os.path.join(resultDir, modelFilename)
	optimal_RoC_Point["modelFilepath"]=modelFilepath
	with open(modelFilepath, "w") as mFile:
		mFile.write(str(optimal_RoC_Point["T"])+"\n")
		mFile.write(detectorsTag+"\n")
		mFile.write(datasetsTag+"\n")
	
	if Debug:
		print("[TPRs]")
		print(TPRs)
		print("[FPRs]")
		print(FPRs)

#	Plotting
	RoCCurveFilePath=os.path.join(resultDir, "RoC_"+detectorsTag+"_"+datasetsTag+".png")
	lineTag = targetModelTag+"+\n"+auxModelTag+"\nAUC="+str(round(AuC,4))
	curvePlot(FPRs, TPRs, "FPR", "TPR", RoCCurveFilePath, lineTag, "ROC Curve")

	return optimal_RoC_Point

def similarityScoreCalTest(textfile1, textfile2):
	dict1=loadRefFile(textfile1)
	scores={}
	with open(os.path.join(textfile2),"rt") as targetFile:
		for line in targetFile:
			parts = line.split()
			scores[parts[0].strip()]=phonetic_similarity(dict1[parts[0].strip()],' '.join(parts[1:]))

	return scores



def thresholdingTest(scoresAE, scoresBenign, T, fileOfFalseCases, fileOfTrueCases):
	falseCases=open(fileOfFalseCases, "w")
	positiveCases=open(fileOfTrueCases, "w")
	totalAEs=len(scoresAE)
	totalBenign=len(scoresBenign)
	TPs, FNs, TNs, FPs=0,0,0,0
	# process scoresAE - TPs and FNs
	for key in scoresAE:
		if scoresAE[key] >= T:
			FNs+=1
			falseCases.write("[FN] fileID: "+key+", score: "+str(scoresAE[key])+"\n")
		else:
			TPs+=1
			positiveCases.write("[TP] fileID: "+key+", score: "+str(scoresAE[key])+"\n")

	# process scoresBenign - TNs and FPs
	for key in scoresBenign:
		if scoresBenign[key] >= T:
			TNs+=1
			positiveCases.write("[TN] fileID: "+key+", score: "+str(scoresBenign[key])+"\n")
		else:
			FPs+=1
			falseCases.write("[FP] fileID: "+key+", score: "+str(scoresBenign[key])+"\n")
	falseCases.close()
	positiveCases.close()
	return [TPs, FNs, TNs, FPs]

def test(
	modelFile,
	recogAEFile1, 
	recogAEFile2, 
	recogBenignFile1, 
	recogBenignFile2, 
	resultDir):

	testResult={}
	if not os.path.exists(resultDir):
		os.makedirs(resultDir)

	scoresAE=similarityScoreCalTest(recogAEFile1,recogAEFile2)
	scoresBenign=similarityScoreCalTest(recogBenignFile1,recogBenignFile2)
	
	with open(os.path.join(modelFile)) as mFile:
		for index, line in enumerate(mFile):
			if index == 0:
				threshold = float(line.strip())
			elif index == 1:
				detectorsTag = line.strip()
			elif index == 2:
				datasetsTag = line.strip()
			else:
				pass
		if index != 2:
			print("\n========================================================================================================")
			print("\n[Model Error]: a model should contains 3 lines. But the input model file has " + str(index+1) + " lines.")
			print("\n========================================================================================================")
			exit(1)

	summaryFile=open(os.path.join(resultDir, "testResult_"+str(threshold)+"_"+detectorsTag+"_"+datasetsTag+".txt"), "w")
	fileOfFalseCases=os.path.join(resultDir, "FalseCaseStudy_Testing_"+str(threshold)+"_"+detectorsTag+"_"+datasetsTag+".txt")
	fileOfTrueCases=os.path.join(resultDir, "TrueCaseStudy_Testing_"+str(threshold)+"_"+detectorsTag+"_"+datasetsTag+".txt")

	[TPs,FNs,TNs,FPs]=thresholdingTest(scoresAE, scoresBenign, threshold, fileOfFalseCases, fileOfTrueCases)

	TPR=round((1.0*TPs)/(TPs+FNs),4)
	FPR=round((1.0*FPs)/(TNs+FPs),4)

	Accuracy=round(1.0*(TPs+TNs)/(TPs+FPs+TNs+FNs), 4)
	summaryFile.write(str(threshold)+"/Threshold, "+str(TPs)+"/TPs, "+str(FNs)+"/FNs, "+str(TNs)+"/TNs, "+str(FPs)+"/FPs, "+str(TPR)+"/TPR, "+str(FPR)+"/FPR, "+str(Accuracy)+"/Accuracy\n")
	summaryFile.close()

	testResult["TPs"]=TPs
	testResult["FNs"]=FNs
	testResult["TNs"]=TNs
	testResult["FPs"]=FPs
	testResult["TPR"]=TPR
	testResult["FPR"]=FPR
	testResult["Accuracy"]=Accuracy

	return testResult
