## A.	Single-Auxiliary-ASR detection systems

For each of the three single-auxiliary-ASR detection systems, *DS0+{DS1}*, *DS0+{GCS}* and *DS0+{AT}*, **use all benign samples to train a system** such that the system's FPR is up-bounded by a given FPR and then **test the system with all AEs**. Run with the script, **train_1am_system_then_test_over_unseen_AEs.bash**. For example,

```Bash
	./train_1am_system_then_test_over_unseen_AEs.bash \
		result_dir \
		unseenAEs \
		0.04 \
		transcriptions_dir
```

Here, "*result_dir*" is the root directory that holds all unseen-AEs-attack experiments. "*unseenAEs*" is the prefix of the directory that holds experimental results for the given FPR 0.04. "0.04" is the given maximum FPR. After running the above command, a directory named "*unseenAEs_givenFPR0.04*" will be generated inside "result_dir" to hold the experimental results for this run.

"*transcriptions_dir*" should have the two sub-directories, "**Train**" and "**unseenAEs**". Inside each of the two sub-directories, there should be four directories:

  * "*AmazonTranscribe*"
  * "*DeepSpeech0.1.0*"
  * "*DeepSpeech0.1.1*"
  * "*GoogleCloudSpeech*"

For each of the above four directories, if it locates in "Train", it should have the text file, "**recogBenignTexts**"; if it locates in "unseenAEs", it should have the text file, "**recogAETexts**". "recogAETexts" file contains AEs' transcriptions recognized by the corresponding ASR, while "recogBenignTexts" file contains benign samples' transcriptions recognized by the corresponding ASR. Each line of either "recogAETexts" or "recogBenignTexts" has the format of "*filename_without_file_extension transcription*". An simple illustration of the structure of "*transcriptions_dir*" is as follows:

  * transcriptions_dir
    - Train
      - AmazonTranscribe
        + recogBenignTexts
      - .......
     - unseenAEs
       - AmazonTranscribe
         + recogAETexts
       - .......	
	

Retrieve experiment result: assume the given FPR is 0.05, then inside "**result_dir/unseenAEs_givenFPR0.05**", you will find three summary files as follows.
   * summary_DeepSpeech0.1.0+AmazonTranscribe.txt
   * summary_DeepSpeech0.1.0+DeepSpeech0.1.1.txt
   * summary_DeepSpeech0.1.0+GoogleCloudSpeech.txt
   
In each of the three summary files, you will find the reported performence like below.
   * givenFPR, Threshold, FPR, FNS, FNR, TPR
   * 0.05, 0.85, 0.0392, 2, 0.0008, 0.9992

## B. Multiple-Auxiliary-ASRs detection systems

For each of the four multiple-auxiliary-ASRs detection systems, *DS0+{DS1, GCS}*, *DS0+{DS1, AT}*, *DS0+{GCS, AT}* and *DS0+{DS1, GCS, AT}*, use "**train_mam_system_then_test_over_unseen_AEs.bash**" to train the deteciton system with benign samples and *one set* of AEs (**either whitebox AE or blackbox AE**), and then use it to detect *the other set* of unseen AEs.

```Bash
	train_mam_system_then_test_over_unseen_AEs.bash \
		result_dir \
		transcriptions_dir \
		similarity_scores_and_feature_vectors_dir
```

"*similarity_scores_and_feature_vectors_dir*" holds the similarity scores and feature vectors that are calculated by the script based on transcriptions inside "*transcriptions_dir*". 

"*transcriptions_dir*" should have the two sub-directories, "**Train**" and "**unseenAEs**". Inside each of the two sub-directories, there should be four directories:

  * "*AmazonTranscribe*"
  * "*DeepSpeech0.1.0*"
  * "*DeepSpeech0.1.1*"
  * "*GoogleCloudSpeech*"

For each of these four directories, if it locates in "**Train**", it should have two files, "**recogAETexts**" and "**recogBenignTexts**"; if it locates in "**unseenAEs**", it should have only one text file, "**recogAETexts**". "recogAETexts" file contains AEs' transcriptions recognized by the corresponding ASR, while "recogBenignTexts" file contains benign samples' transcriptions recognized by the corresponding ASR. Each line of either "recogAETexts" or "recogBenignTexts" has the format of "filename_without_file_extension transcription". An simple illustration of the structure of transcriptions_dir is as follows:

  * transcriptions_dir
    - Train
      - AmazonTranscribe
        + recogAETexts
        + recogBenignTexts
      - .......
     - unseenAEs
       - AmazonTranscribe
         + recogAETexts
       - .......
       
**Retrieve experiment result**: the summary is stored in "**UnseenAE_result_summary.txt**" inside "**result_dir**". An example of the content is as below.
   * PhoneticEncodedJaroWinkler-DeepSpeech0.1.1_GoogleCloudSpeech# FNR: 0.0067, FNs: 4, TPR: 0.9933
   * PhoneticEncodedJaroWinkler-DeepSpeech0.1.1_AmazonTranscribe# FNR: 0.0083, FNs: 5, TPR: 0.9917
   * PhoneticEncodedJaroWinkler-GoogleCloudSpeech_AmazonTranscribe# FNR: 0.0067, FNs: 4, TPR: 0.9933
   * PhoneticEncodedJaroWinkler-DeepSpeech0.1.1_GoogleCloudSpeech_AmazonTranscribe# FNR: 0.0083, FNs: 5, TPR: 0.9917


### B1. use benign samples and white-box AEs to train the system and then use black-box AEs (unseen during training process) to test the system.

```Bash
	train_mam_system_then_test_over_unseen_AEs.bash \
		result_dir \
		transcriptions_unseen_blackbox_AE_dir \
		similarity_score_and_feature_vector_dir
```

### B2. use benign samples and black-box AEs to train the system and then use white-box AEs (unseen during training process) to test the system.

```Bash
	train_mam_system_then_test_over_unseen_AEs.bash \
		result_dir \
		transcriptions_unseen_whitebox_AE_dir \
		similarity_score_and_feature_vector_dir		
```
