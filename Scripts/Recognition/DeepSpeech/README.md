* Function:	recognize audio files inside <audio_dataset_dir> and place the recognition results and logs into two files inside <working_dir>

* Usage:  python3 <this script> <audio_dataset_dir> <working_dir> <detector_name> <dataset_name> <deepspeech_model_dir>

* Notes:
*			1. 	DeepSpeech (https://github.com/mozilla/DeepSpeech) model files are needed.
*				They are "output_graph.pb", "alphabet.txt", "alphabet.txt", "lm.binary" and "trie".
*			2. 	Audio files to recognize should be WAV files. Convert them beforehand if not.
*			3. 	Suggest to create an virtual environment to do recognition.
*			4. 	Install Python packages deepspeech and scipy in advance.


