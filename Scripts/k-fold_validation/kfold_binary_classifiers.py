#!/usr/bin/python3

import sys
import os
import random
import numpy as np
import BinaryClassifierMethods

# Binary Classifiers
Classifiers=["SVM", "KNN", "RandomForest"] 
# Transcription directory name by ASR
ASRNames=["DeepSpeech0.1.0", "DeepSpeech0.1.1", "GoogleCloudSpeech", "AmazonTranscribe"]
# list of Auxiliary-ASRs tags
AuxASRTags=[ASRNames[1],
            ASRNames[2],
            ASRNames[3],
            ASRNames[1]+"_"+ASRNames[2],
            ASRNames[1]+"_"+ASRNames[3],
            ASRNames[2]+"_"+ASRNames[3],
            ASRNames[1]+"_"+ASRNames[2]+"_"+ASRNames[3]]

def usage():
    print("====================================================================================")
    print("<this script> <result directory>  K")
    print("====================================================================================")

def main(argv):

    # [Setup Input Arguments]
    if len(argv) != 2:
        print("[Error] the number of arguments should be 2, but is {}.".format(len(argv)))
        usage()
        exit(1)


    resultDir=argv[0]
    k=int(argv[1])

    datasetsDir=os.path.join(resultDir, "datasets")
    experimentRoot=os.path.join(resultDir, "k-fold_experiment_result")
    if not os.path.exists(experimentRoot):
        os.makedirs(experimentRoot)

    topLevelSummaryFilePath=os.path.join(experimentRoot, "summary")
    allSummaries={}
    for cls in Classifiers:
        clsDir=os.path.join(experimentRoot, cls)
        if not os.path.exists(clsDir):
            os.makedirs(clsDir)
        clsSummaryFilePath=os.path.join(clsDir, "summary")
        clsSummary=[]
        for auxTag in AuxASRTags:
            print("\n==Experiment with the system DS0+"+auxTag)
            auxTagDir=os.path.join(clsDir, auxTag)
            if not os.path.exists(auxTagDir):
                os.makedirs(auxTagDir)
            summaryFilePath=os.path.join(auxTagDir, "summary") 
            allTestResults={"TPs":[], "FNs":[], "TNs":[], "FPs":[],"FNR":[], "FPR":[], "Accuracy":[]}
            for currentK in range(1, k+1):
                print("===Running with the {}th dataset".format(currentK))
                currentFVDir=os.path.join(datasetsDir, str(currentK)+"/feature_vectors")
                currentResultDir=os.path.join(auxTagDir, str(currentK))
                if not os.path.exists(currentResultDir):
                    os.makedirs(currentResultDir)
                AETrainPath=os.path.join(currentFVDir, "feature_vectors_PhoneticEncodedJaroWinkler_AE_Train_"+auxTag+".txt")
                BenignTrainPath=os.path.join(currentFVDir, "feature_vectors_PhoneticEncodedJaroWinkler_Benign_Train_"+auxTag+".txt")
                AETestPath=os.path.join(currentFVDir, "feature_vectors_PhoneticEncodedJaroWinkler_AE_Test_"+auxTag+".txt")
                BenignTestPath=os.path.join(currentFVDir, "feature_vectors_PhoneticEncodedJaroWinkler_Benign_Test_"+auxTag+".txt")

                modelFilepath=os.path.join(currentResultDir, "model_"+cls+"_"+auxTag)
                testResult=BinaryClassifierMethods.trainAndtest(
                    AETrainPath,
                    BenignTrainPath,
                    AETestPath,
                    BenignTestPath,
                    cls,
                    auxTag,
                    "PhoneticEncodedJaroWinkler",
                    currentResultDir,
                    modelFilepath)
                allTestResults["TPs"].append(testResult["TPs"])
                allTestResults["FNs"].append(testResult["FNs"])
                allTestResults["TNs"].append(testResult["TNs"])
                allTestResults["FPs"].append(testResult["FPs"])
                allTestResults["FNR"].append(testResult["FNR"])           
                allTestResults["FPR"].append(testResult["FPR"])
                allTestResults["Accuracy"].append(testResult["Accuracy"])

            print("\t[System Summary Section]")
            with open(summaryFilePath, "w+") as sf:
                # report testing summary
                sf.write("[Testing Summary]\n")
                testingSummary="TPs:"+str(round(np.mean(allTestResults["TPs"]), 1))+"/"+str(round(np.std(allTestResults["TPs"]), 4))
                testingSummary+=", FNs:"+str(round(np.mean(allTestResults["FNs"]), 1))+"/"+str(round(np.std(allTestResults["FNs"]), 4))
                testingSummary+=", TNs:"+str(round(np.mean(allTestResults["TNs"]), 1))+"/"+str(round(np.std(allTestResults["TNs"]), 4))
                testingSummary+=", FPs:"+str(round(np.mean(allTestResults["FPs"]), 1))+"/"+str(round(np.std(allTestResults["FPs"]), 4))
                testingSummary+=", FNR:"+str(round(np.mean(allTestResults["FNR"]), 4))+"/"+str(round(np.std(allTestResults["FNR"]), 4))
                testingSummary+=", FPR:"+str(round(np.mean(allTestResults["FPR"]), 4))+"/"+str(round(np.std(allTestResults["FPR"]), 4))
                testingSummary+=", Accuracy:"+str(round(np.mean(allTestResults["Accuracy"]), 4))+"/"+str(round(np.std(allTestResults["Accuracy"]), 4))
                sf.write(testingSummary+"\n")
                print("\ttestingSummary: " + testingSummary)
                clsSummary.append("[auxASRs:"+auxTag+"] "+testingSummary)

        print("\n\tsummary of different systems using the same classifier: "+cls)
        with open(clsSummaryFilePath, "w+") as sf:
            for summary in clsSummary:
                sf.write(summary+"\n")
                print("\\t"+summary)
       
        allSummaries[cls]=clsSummary 

    print("\n\t[All summaries]")
    with open(topLevelSummaryFilePath, "w+") as sf:
        for key, value in allSummaries.items():
            print("\t\t["+key+"]")
            sf.write("["+key+"]\n")
            for summary in value:
                print("\t\t"+summary)
                sf.write(summary+"\n")
            print("")
            sf.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
