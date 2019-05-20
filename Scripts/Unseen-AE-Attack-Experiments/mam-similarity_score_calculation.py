import os.path
import sys
import collections
import getopt
import jellyfish
import re
import math
from collections import Counter

Debug=False

def jaro_winkler_sim(str1, str2):
	return jellyfish.jaro_winkler(str1, str2)


def phonetic_encoded_jaro_winkler_sim(ref, result):
	targetTmp = jellyfish.metaphone(result)
	refTmp = jellyfish.metaphone(ref)
	if Debug:	
		print ("Result: \t\t" + result)
		print ("Converted result: \t" + targetTmp)
		print ("Ref: \t\t\t" + ref)
		print ("Converted ref: \t\t" + refTmp)
		print ("------------------------------------------------------------------------------")
	return jellyfish.jaro_winkler(refTmp, targetTmp)

def jaccard_sim(str1, str2): 
	a = set(str1.split()) 
	b = set(str2.split())
	c = a.intersection(b)
	return float(len(c)) / (len(a) + len(b) - len(c))

def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def text_to_vector(text):
    word = re.compile(r'\w+')
    words = word.findall(text)
    return Counter(words)

def cosine_sim(str1, str2): 
	return get_cosine(text_to_vector(str1),text_to_vector(str2))

def phonetic_encoded_cosine_sim(str1, str2):
	targetTmp = jellyfish.metaphone(str2)
	refTmp = jellyfish.metaphone(str1)
	if Debug:
		print ("Result: \t\t" + str2)
		print ("Converted result: \t" + targetTmp)
		print ("Ref: \t\t\t" + str1)
		print ("Converted ref: \t\t" + refTmp)
		print ("------------------------------------------------------------------------------")

	return cosine_sim(refTmp, targetTmp)

def phonetic_encoded_jaccard_sim(str1, str2):
	targetTmp = jellyfish.metaphone(str2)
	refTmp = jellyfish.metaphone(str1)
	if Debug:	
		print ("Result: \t\t" + str2)
		print ("Converted result: \t" + targetTmp)
		print ("Ref: \t\t\t" + str1)
		print ("Converted ref: \t\t" + refTmp)
		print ("------------------------------------------------------------------------------")

	return jaccard_sim(refTmp, targetTmp)

similarity_cal_methods={"Jaccard":jaccard_sim, "Cosine":cosine_sim, "JaroWinkler":jaro_winkler_sim, "PhoneticEncodedJaccard":phonetic_encoded_jaccard_sim, "PhoneticEncodedCosine":phonetic_encoded_cosine_sim, "PhoneticEncodedJaroWinkler":phonetic_encoded_jaro_winkler_sim}

def loadRefFile(filepath):
	refDict={}
	print ('\tWorking on ref file: ' + filepath)
	with open(os.path.join(filepath),"rt") as targetFile:
		for line in targetFile:
			parts = line.split()
			refDict[parts[0].strip()] = ' '.join(parts[1:])
	return refDict

# Each line of both of the input files, 'textfile1' and 'textfile2',
# has the following format:
# 	<filename without file extension> : <recognized transcription>
#
# Each line of the output file:
# 	<filename without file extension> : <similarity score> 
def similarityScoreCal(textfile1, textfile2, outputFilePath, sim_cal_method_id):
	outputFile=open(outputFilePath, "w")
	dict1=loadRefFile(textfile1)
	with open(os.path.join(textfile2),"rt") as targetFile:
		for line in targetFile:
			parts = line.split()
			if Debug:
				print(dict1[parts[0].strip()])
				print(parts[1:])
				scores.append(phonetic_similarity(dict1[parts[0].strip()],' '.join(parts[1:])))
				scores[parts[0].strip()]=phonetic_similarity(dict1[parts[0].strip()],' '.join(parts[1:]))
			score=similarity_cal_methods[sim_cal_method_id](dict1[parts[0].strip()], ' '.join(parts[1:]))
			outputFile.write(parts[0].strip()+":"+str(round(score, 4))+"\n")

	outputFile.close()

def main(argv):
	isAE='' # Yes or No
	isForTraining='' # Yes or No
	detectorsTag='' # detector1_detector2, e.g., DS0_DS1
	recogFilePath1=''
	recogFilePath2=''
	if len(argv) != 7:
		print("\n==============================================================================================================")
		print("\nUsage: python <this_script> isAE isForTraining detectorsTag recogFilePath1 recogFilePath2 resultDir sim_cal_id")
		print("\n==============================================================================================================")
		return


	isAE = argv[0].strip()
	isForTraining = argv[1].strip()
	detectorsTag=argv[2].strip()
	recogFilePath1 = argv[3].strip() 
	recogFilePath2 = argv[4].strip() 
	resultDir=argv[5].strip()
	sim_cal_id=argv[6].strip()

	if not os.path.exists(resultDir):
		os.makedirs(resultDir)

	outputFileName=sim_cal_id+"_"
	if isAE == "Yes":
		outputFileName+="AE"
	else:
		outputFileName+="Benign"

	if isForTraining == "Yes":
		outputFileName+="_Train"
	else:
		outputFileName+="_Unseen"

	outputFileName+="_"+detectorsTag+".txt"

	similarityScoreCal(recogFilePath1, recogFilePath2, os.path.join(resultDir,outputFileName), sim_cal_id)

main(sys.argv[1:])
