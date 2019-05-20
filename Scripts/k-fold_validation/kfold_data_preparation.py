#!/usr/bin/python3

import sys
import os
import random
import subprocess

# Transcription directory name by ASR
transcriptionSubDirNames=["DeepSpeech0.1.0", "DeepSpeech0.1.1", "AmazonTranscribe", "GoogleCloudSpeech"]

#fvScriptDir="Feature-Generation"
#fvCreationScript="./run.bash"

def usage():
    print("====================================================================================")
    print("<this script> <original transcription directory> <result directory> <dataset size> K")
    print("====================================================================================")

def main(argv):

    # [Setup Input Arguments]
    if len(argv) != 4:
        print("[Error] the number of arguments should be 4, but is {}.".format(len(argv)))
        usage()
        exit(1)


    transcriptionDir=argv[0]
    resultDir=argv[1]
    datasetSize=int(argv[2])
    k=int(argv[3])

    datasetsPath=os.path.join(resultDir, "datasets")

    # [Dataset Preparation]
    # Split the original transcriptions into k folds and then create k datasets
    # inside <resultDir>/datasets, each of which contains (k-1) folds
    # as training set and 1 fold as testing set.

    # data loading and separation 
    cntInOneFold=datasetSize//k # the last fold may has a few more samples than the rest
    allTranscriptions=[{}, {}, {}, {}]
    AEIndices=list(range(0, datasetSize))
    BSIndices=list(range(0, datasetSize))
    random.shuffle(AEIndices)
    random.shuffle(BSIndices)
    for (subDirName, transcriptions) in zip(transcriptionSubDirNames, allTranscriptions):
        with open(os.path.join(transcriptionDir, subDirName+"/recogAETexts")) as AEFile, open(os.path.join(transcriptionDir, subDirName+"/recogBenignTexts")) as BSFile:
            AETranscriptions=[]
            BSTranscriptions=[]
            for lineAE in AEFile:
                AETranscriptions.append(lineAE)
            for lineBS in BSFile:
                BSTranscriptions.append(lineBS)
            transcriptions["AE"]={}
            transcriptions["BS"]={}
            for currentK in range(1, k):
                transcriptions["AE"][currentK]=[ AETranscriptions[i] for i in AEIndices[cntInOneFold*(currentK-1):cntInOneFold*currentK] ]
                transcriptions["BS"][currentK]=[ BSTranscriptions[i] for i in BSIndices[cntInOneFold*(currentK-1):cntInOneFold*currentK] ]
                
            transcriptions["AE"][k]=[ AETranscriptions[i] for i in AEIndices[cntInOneFold*(k-1):] ]
            transcriptions["BS"][k]=[ BSTranscriptions[i] for i in BSIndices[cntInOneFold*(k-1):] ]

    # compose each dataset   
    for currentK in range(1, k+1):
        print("Create the {}th dataset".format(currentK))
        currentDir=os.path.join(datasetsPath, str(currentK))
        if not os.path.exists(currentDir):
            os.makedirs(currentDir)
        testDir=os.path.join(currentDir, "Test")
        trainDir=os.path.join(currentDir, "Train")
        if not os.path.exists(testDir):
            os.makedirs(testDir)
        if not os.path.exists(trainDir):
            os.makedirs(trainDir)
        for (subDirName, transcriptions) in zip(transcriptionSubDirNames, allTranscriptions):
            testASRDir=os.path.join(testDir, subDirName)
            trainASRDir=os.path.join(trainDir, subDirName)
            if not os.path.exists(testASRDir):
                os.makedirs(testASRDir)
            if not os.path.exists(trainASRDir):
                os.makedirs(trainASRDir)
            testASRAEFile=os.path.join(testASRDir, "recogAETexts")
            testASRBSFile=os.path.join(testASRDir, "recogBenignTexts")
            trainASRAEFile=os.path.join(trainASRDir, "recogAETexts")
            trainASRBSFile=os.path.join(trainASRDir, "recogBenignTexts")
            for runningK in range(1, k+1):
                if runningK == currentK:
                    with open(testASRAEFile, "a+") as aef, open(testASRBSFile, "a+") as bsf:
                        for item in transcriptions["AE"][runningK]:
                            aef.write(item)
                        for item in transcriptions["BS"][runningK]:
                            bsf.write(item)
                else:
                    with open(trainASRAEFile, "a+") as aef, open(trainASRBSFile, "a+") as bsf:
                        for item in transcriptions["AE"][runningK]:
                            aef.write(item)
                        for item in transcriptions["BS"][runningK]:
                            bsf.write(item)         

#    for currentK in range(1, k+1):
#        print("Process the {}th dataset".format(currentK))
#        currentDir=os.path.join(datasetsPath, str(currentK))
#        # create feature vectors of the current dataset, which will be used when training and testing multiple-aux-ASRs systems
#        cwd=os.getcwd()
#        print("[Start: create feature vectors]")
#        os.chdir(os.path.join(cwd, fvScriptDir))
#        subprocess.Popen([fvCreationScript, currentDir, currentDir])
#        os.chdir(cwd)
#        print("[Finished: the creation of feature vectors]")

if __name__ == "__main__":
    main(sys.argv[1:])
