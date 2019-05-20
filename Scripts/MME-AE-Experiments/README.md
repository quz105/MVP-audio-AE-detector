1. Experiment Preparation
   - A.	Create a directory (say **result_dir**) for holding all experimental results, similarity scores and feature vectors.
   - B.	**ss_fv_dir** (inside *result_dir*): directory that contains all necessary similarity scores and feature vectors. Six similarity-score files and real AEs' and benign samples' feature-vector files should be prepared in advance. Each of similarity-score files contains similarity scores of each audio's transcriptions recognized by DS0 and another ASR indicated by the filename. And the type of audios, either "AE" (Adversarial Example) or "Benign" (Benign Sample), is also indicated in the filename. Use "**featureGeneration_MMEHypotheticalAE.py**" to create **8** feature-vector files.
   
     [Inside ss_fv_dir directory]
     
     - 6 similarity-score files ()
       - AE_AT.txt
       - AE_DS1.txt
       - AE_GCS.txt
       - Benign_AT.txt
       - Benign_DS1.txt
       - Benign_GCS.txt
     - Real AEs' and benign samples' feature-vector files
       - real AEs            :   "fv_SME_AE_DS0"
       - real bening samples :   "fv_Real_BS_<num_of_benign_samples>"
     - feature-vector filenames for 7 types of hypothetical AEs
       - 2-ASRs-effective AEs:   "fv_MME_AE_DS0_AT",  "fv_MME_AE_DS0_DS1", "fv_MME_AE_DS0_GCS"
       - 3-ASRs-effective AEs:   "fv_MME_AE_DS0_DS1_AT", "fv_MME_AE_DS0_DS1_GCS",  "fv_MME_AE_DS0_GCS_AT"
       - Comprehensive AEs   :   "fv_Comprehensive_AE" (an assembly of feature vectors of all 3-ASRs-effective AEs)
     - feature-vector filename for benign samples:
       - Comprehensive BSs   :   "fv_Comprehensive_BS_<3 X num_of_benign_samples>"

2. Run the experiment

```
   run.bash result_dir ss_fv_dir
```

3. **Retrieve experiment Result**
   - A.	8 detection systems will be built and tested. For each detection system, a fold named with the corresponding AEs' type will be created inside "**result_dir**", where the result of building and testing the detection system upon unused types of AEs will be recorded.
   - B.	8 AE_types
        - real AEs            :   "SME_AE_DS0"
        - 2-ASRs-effective AEs:   "MME_AE_DS0_AT",  "MME_AE_DS0_DS1", "MME_AE_DS0_GCS"
        - 3-ASRs-effective AEs:   "MME_AE_DS0_DS1_AT", "MME_AE_DS0_DS1_GCS",  "MME_AE_DS0_GCS_AT"
        - Comprehensive AEs   :   "Comprehensive_AE" (an assembly of all 3-ASRs-effective AEs)	
   - C.	Retrieve a summary of experimental results
   
     The summary contains:
      - Experimental Result on Testing dataset For Each Type of MAE AEs
      -	Result of Testing Each Detection System With Real AEs
      - Result of Testing Detector~>{DS0, DS1, GCS} with AE(DS0, DS1) and AE(DS0, GCS)
      - Result of Testing Detector~>{DS0, DS1, AT} with AE(DS0, DS1) and AE(DS0, AT)
      - Result of Testing Detector~>{DS0, GCS, AT} with AE(DS0, GCS) and AE(DS0, AT)
      - Result of Testing Detector built upon Comprehensive AEs with Real AE, AE(DS0, DS1), AE(DS0, GCS) and AE(DS0, AT)
   
     Run:
     ```Bash
     retrieve_summary.bash result_dir
     ```
