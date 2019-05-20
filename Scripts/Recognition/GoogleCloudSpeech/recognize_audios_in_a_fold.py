import io
import os
import sys
import re
import collections
import time
import sys

# Imports the Google Cloud client library
import google.auth
import google.auth.transport.requests
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from os import listdir
from os.path import isfile, join
from os import walk


def GoogleCloudSpeech(filename):	
	
# Refreash the credentials before every request to avoid race conditions	
	credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
	credentials.refresh(google.auth.transport.requests.Request())	
# Instantiates a client
	client = speech.SpeechClient(credentials=credentials)

# The name of the audio file to transcribe
	filepath = os.path.join(
		os.path.dirname(__file__),
		'',
		str(filename))

# Loads the audio into memory
	with io.open(filepath, 'rb') as audio_file:
		content = audio_file.read()
		audio = types.RecognitionAudio(content=content)
		audio_file.close()

	config = types.RecognitionConfig(
		encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
		sample_rate_hertz=16000,
		language_code='en-US')

# Detects speech in the audio file
	response = client.recognize(config, audio)

	for result in response.results:
		print('Transcription: {}'.format(result.alternatives[0].transcript.upper()))
		return 	result.alternatives[0].transcript.upper()

def usage():
    print("[Usage]")
    print("\tpython <this script> <audioDatasetDir> <datasetName> <googleAPPCredential> <resultDir>")
    print("\t<audioDatasetDir>: contain only WAV files")
    print("\t<datasetName>: used for categorizing resulting files' names")

def main(argv):
    if len(argv) != 4:
        usage()
        sys.exit(2)

    audioDatasetDir = argv[0].strip()
    datasetName=argv[1].strip()
    googleApplicationCredential=argv[2].strip()
    resultDir=argv[3].strip()

    print('Audio dataset directory: '+audioDatasetDir)
    print('Name of testing dataset: ' + datasetName)
    print('GoogleApplicationCredential: ' + googleApplicationCredential)
    print('Result directory: ' + resultDir)

    detectorName="GCS"    
    timeStamp = time.strftime("%Y%m%d-%H%M%S")

    recTextsFile=os.path.join(resultDir, detectorName+"_"+datasetName+"_"+timeStamp+"_recTexts.txt")
    recLogFile=os.path.join(resultDir, detectorName+"_"+datasetName+"_"+timeStamp+"_recLog.txt")

    recFailures=0
    recPasses=0
    total=0

    os.environ['GOOGLE_APPLICATION_CREDENTIALS']=googleApplicationCredential

    with open(recLogFile, "w+") as log, open(recTextsFile, "w+") as recogs:
        cnt=1
        for (dirpath, dirnames, filenames) in walk(audioDatasetDir):
            for filename in filenames:
                total+=1
                audioFilePath=os.path.join(audioDatasetDir, filename)
                print("["+str(cnt)+"] Processing "+audioFilePath)
                transcript = ''
                logInfo="["+str(cnt)+"] "+str(filename)
                try:
                    transcript = GoogleCloudSpeech(audioFilePath)
                    recPasses+=1
                except:
                    recFailures+=1
                    e = sys.exc_info()[0]
                    print(' Exceptions: '+str(e))
                    logInfo=logInfo+' Exceptions: '+str(e)
                cnt+=1
                log.write(logInfo+"\n")
                recogs.write(re.sub(".wav","",filename)+' '+str(transcript)+'\n')

            testStatistics="Total: "+str(total)+", Passes: "+str(recPasses)+", Failures: "+str(recFailures)
            print("[Summary] "+testStatistics)
            log.write("[Summary] "+testStatistics+"\n")
            log.write('[Dataset directory] '+audioDatasetDir+"\n")
            log.write('[Name of testing dataset] ' + datasetName+"\n")



main(sys.argv[1:])

