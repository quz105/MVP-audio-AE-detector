# Function:	recognize audio files inside <audio_dataset_dir> and place the recognition results and logs into two files inside <working_dir>
#
# Usage:  python3 <this script> <audio_dataset_dir> <working_dir> <detector_name> <dataset_name> <deepspeech_model_dir>
#
# Notes:
#			1. 	DeepSpeech (https://github.com/mozilla/DeepSpeech) model files are needed.
#				They are "output_graph.pb", "alphabet.txt", "alphabet.txt", "lm.binary" and "trie".
#			2. 	Audio files to recognize should be WAV files. Convert them beforehand if not.
#			3. 	Suggest to create an virtual environment to do recognition.
#			4. 	Install Python packages deepspeech and scipy in advance.


import os
import os.path
import sys
import re
import time
from os import walk

from deepspeech.model import Model
import scipy.io.wavfile as wav

def ASR(audiofile, ds):
	fs, audio = wav.read(audiofile)
	processed_data = ds.stt(audio, fs)
	return processed_data


def recognition(audio_dataset_dir, default_model_dir):

	Debug=True

	# == [Configure DeepSpeech's Parameters] ==
	# These constants control the beam search decoder

	# Beam width used in the CTC decoder when building candidate transcriptions
	BEAM_WIDTH = 500

	# The alpha hyperparameter of the CTC decoder. Language Model weight
	LM_WEIGHT = 1.75

	# The beta hyperparameter of the CTC decoder. Word insertion weight (penalty)
	WORD_COUNT_WEIGHT = 1.00

	# Valid word insertion weight. This is used to lessen the word insertion penalty
	# when the inserted word is part of the vocabulary
	VALID_WORD_COUNT_WEIGHT = 1.00


	# These constants are tied to the shape of the graph used (changing them changes
	# the geometry of the first layer), so make sure you use the same constants that
	# were used during training

	# Number of MFCC features to use
	N_FEATURES = 26

	# Size of the context window used for producing timesteps in the input vector
	N_CONTEXT = 9
	# == [Configure DeepSpeech's Parameters] ==


	# == [Setup parameters] ==
	ds = Model(default_model_dir+"/output_graph.pb", N_FEATURES, N_CONTEXT, default_model_dir+"/alphabet.txt", BEAM_WIDTH)
	ds.enableDecoderWithLM(default_model_dir+"/alphabet.txt", default_model_dir+"/lm.binary", default_model_dir+"/trie", LM_WEIGHT,WORD_COUNT_WEIGHT, VALID_WORD_COUNT_WEIGHT)

	# == [Recognition] ==
	transcriptions={}
	aveTimeCost=0.0
	cnt=0
	tcosts=[]
	startTime=time.process_time()
	for (dirpath, dirnames, filenames) in walk(audio_dataset_dir):
		for filename in sorted(filenames):
			cnt+=1
			transcription=''
			audiopath=os.path.join(audio_dataset_dir,filename)
			singleStart=time.process_time()
			transcription=ASR(audiopath, ds)
			tcosts.append(time.process_time() - singleStart)
			fileID=re.sub(".wav","",filename)
			#if Debug:
			print(fileID+": "+transcription)
			transcriptions[fileID]=transcription.upper()

	endTime=time.process_time()
	aveTimeCost=round((endTime-startTime)/cnt, 6)
	print("start:"+str(startTime)+", end:"+str(endTime)+", aveTimeCost:"+str(aveTimeCost)+", cnt:"+str(cnt)+"\n")
	#for cost in tcosts:
	#	print(str(cost))
	return transcriptions, aveTimeCost, tcosts
