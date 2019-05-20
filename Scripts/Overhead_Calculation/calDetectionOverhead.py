#!/usr/bin/python3

import os
import sys
import time
import DeepSpeech_Recog
import jellyfish
import pickle

def phonetic_similarity(ref, result):
    targetTmp = result
    refTmp = ref
    targetTmp = jellyfish.metaphone(result)
    refTmp = jellyfish.metaphone(ref)

    return jellyfish.jaro_winkler(refTmp, targetTmp)



def similarityScoreCal(transcriptions1, transcriptions2):
    scores=[]
    for key, transcription in transcriptions1.items():
        scores.append(phonetic_similarity(transcription, transcriptions2[key]))
    return scores

def mean(inputList):
    total=0.0
    for item in inputList:
        total+=item
    average=round(total/len(inputList), 8)
    return average



audio_dataset_dir=sys.argv[1]
DS0_model_dir=sys.argv[2]
DS1_model_dir=sys.argv[3]
model_filepath=sys.argv[4]
# model to load: DS0+{DS1} - SVM
loadedModel=pickle.load(open(model_filepath, "rb"))

# calculate overhead of ASR recognition
print("[DS0]")
DS0_Transcriptions, DS0_AveCost, DS0_TCosts=DeepSpeech_Recog.recognition(audio_dataset_dir, DS0_model_dir)
print("DS0_AveCost: "+str(DS0_AveCost)+" seconds in average")

print("\n[DS1]")
DS1_Transcriptions, DS1_AveCost, DS1_TCosts=DeepSpeech_Recog.recognition(audio_dataset_dir, DS1_model_dir)
print("DS1_AveCost: "+str(DS1_AveCost)+" seconds in average")

recognitionOverHead=[]
for (T0, T1) in zip(DS0_TCosts, DS1_TCosts):
    actualT=T0
    if T1>T0:
        actualT=T1
    recognitionOverHead.append(actualT-T0)

averageRecogOH=mean(recognitionOverHead)
averageRecogDS0=mean(DS0_TCosts)

# calculate overhead of similarity calculation
startTime=time.process_time()
scores=similarityScoreCal(DS0_Transcriptions, DS1_Transcriptions)
averageSimCalTime=round((time.process_time()-startTime)/len(scores), 8)

# calculate overhead of binary classifier
cnt=1
startTime=time.process_time()
for score in scores:
    print("predict "+str(cnt)+"th sample")
    loadedModel.predict([[score]])
    cnt+=1
averageClassificationTime=round((time.process_time()-startTime)/len(scores), 8)

averageTotalOH=averageRecogOH+averageSimCalTime+averageClassificationTime
summaryFilepath="summary"
with open(os.path.join("./", summaryFilepath), "w+") as sf:
    sf.write("The averaged recognition cost of DS0 over " + str(len(scores)) + " audio samples is: " + str(averageRecogDS0)+"\n")
    sf.write("The reported overheads (seconds / percentage) are averaged from "+str(len(scores))+" audio samples\n")
    sf.write("Recognition: "+str(averageRecogOH)+"/"+str(round(averageRecogOH/averageRecogDS0, 8))+"\n")
    sf.write("Similarity Cal: "+str(averageSimCalTime)+"/"+str(round(averageSimCalTime/averageRecogDS0, 8))+"\n")
    sf.write("Classification: "+str(averageClassificationTime)+"/"+str(round(averageClassificationTime/averageRecogDS0, 8))+"\n")
    sf.write("Total: "+str(averageTotalOH)+"/"+str(round(averageTotalOH/averageRecogDS0, 8))+"\n")

print("The averaged recognition cost of DS0 over " + str(len(scores)) + " audio samples is: " + str(averageRecogDS0))
print("The reported overheads (seconds / percentage) are averaged from "+str(len(scores))+" audio samples\n")
print("Recognition: "+str(averageRecogOH)+"/"+str(round(averageRecogOH/averageRecogDS0, 8)))
print("Similarity Cal: "+str(averageSimCalTime)+"/"+str(round(averageSimCalTime/averageRecogDS0, 8)))
print("Classification: "+str(averageClassificationTime)+"/"+str(round(averageClassificationTime/averageRecogDS0, 8)))
print("Total: "+str(averageTotalOH)+"/"+str(round(averageTotalOH/averageRecogDS0, 8)))

