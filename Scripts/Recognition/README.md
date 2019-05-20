1. 	Recognition using DeepSpeech, Google Cloud Speech and Amazon Transcribe.
	Instructions and scripts are given in directories of DeepSpeech, GoogleCloudSpeech and AmazonTranscribe to do recognition.

2.	Each line of transcription file has the following format:
    - **Filename\_without\_file\_extension transcription**

3.	Structure of Transcription directory that is created by running the recognition scripts.
	There are two "**Test**" and "**Train**" sub-directories inside the root directory. In each of "Test" and "Train" directories, it has the following sturcture. (Take "Test" diretory for example.)
    - RootDirectory
      - Test
        - AmazonTranscribe
        - DeepSpeech0.1.0
        - DeepSpeech0.1.1
        - GoogleCloudSpeech

	
	In each of the four directories, "AmazonTranscribe", "DeepSpeech0.1.0", "DeepSpeech0.1.1" and "GoogleCloudSpeech", there are two files named "**recogAETexts**" and "**recogBenignTexts**". The transcriptions we obtained are put in "Transcriptions" as a reference.
    Based on the resulting transcriptions directory, "Transcriptions", follow the "README.md" in each directory inside "Scripts" direcotyr to create transcriptions directories accordingly.
