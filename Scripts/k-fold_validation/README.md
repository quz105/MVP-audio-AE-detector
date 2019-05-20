Run scripts as the following order
1. prepare the k-folded datasets: ith dataset is placed in the directory, <result directory>/datasets/i
      ./kfold_data_preparation.py <original transcription directory> <result directory> <dataset size> K
      Note: For the original transcriptions used in experiment, please refer to the directory, "./Transcriptions"

2. create feature vectors for each k-folded dataset
      cd ./Feature-Generation
      ./run.bash <datasets root> K
      Note: <datasets root> := <result directory>/datasets

3. k-fold validation for all systems by using one of the three binary classifiers, SVM, KNN and RandomForest
      ./kfold_binary_classifiers.py <result directory> K
      Note: the validation result will be placed inside the directory, <result directory>/"k-fold_experiment_result". Check "summary" in "k-fold_experiment_result" for a brief report.