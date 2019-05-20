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


Debug=False

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


def ASR(audiofile):
	fs, audio = wav.read(audiofile)
	processed_data = ds.stt(audio, fs)
	if Debug:
		print("[Recognition Result] "+processed_data)
	return processed_data



# Input parameters
audio_dataset_dir=sys.argv[1]
working_dir=sys.argv[2]
detector_name=sys.argv[3] # DS0 (DeepSpeech v0.1.0) or DS1 (DeepSpeech v0.1.1)
dataset_name=sys.argv[4]
default_model_dir=sys.argv[5]

# Setup parameters
ds = Model(default_model_dir+"/output_graph.pb", N_FEATURES, N_CONTEXT, default_model_dir+"/alphabet.txt", BEAM_WIDTH)
ds.enableDecoderWithLM(default_model_dir+"/alphabet.txt", default_model_dir+"/lm.binary", default_model_dir+"/trie", LM_WEIGHT,WORD_COUNT_WEIGHT, VALID_WORD_COUNT_WEIGHT)

time_stamp=time.strftime("%Y%m%d-%H%M%S")

rec_texts=os.path.join(working_dir,detector_name+'_'+dataset_name+'_'+time_stamp+'_recTexts.txt')
rec_log=os.path.join(working_dir,detector_name+'_'+dataset_name+'_'+time_stamp+'_recLog.txt')

# Recognition
with open(rec_log, "w+") as log, open(rec_texts, "w+") as recogs:
	cnt=0
	for (dirpath, dirnames, filenames) in walk(audio_dataset_dir):
		for filename in filenames:
			cnt+=1
			log.write("["+str(cnt)+"] processing " + filename + "\n")
			print("["+str(cnt)+"] processing " + filename)
			transcription=''
			if(detector_name=="DS0" or detector_name=="DS1"):
				audiopath=os.path.join(audio_dataset_dir,filename)
				if Debug:
					print("audiopath: "+audiopath)
				transcription=ASR(audiopath)
				if Debug:
					print("trainscription: "+transcription)
				recogs.write(re.sub(".wav","",filename)+" "+transcription.upper()+"\n")

