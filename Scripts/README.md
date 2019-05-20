# Evaluation
## Virtual Environment Setup
0. create a virutal enviroment
```
   mkdir <virtual_env>
   virtualenv <virtual_env>
```
1. Activate the virtual environment
```
    source <virtual_env>/bin/activate
```
2. Dependent Python packages to install
   - numpy
   - sklearn
   - jellyfish
   - matplotlib


## Evaluation Step by Step: run the evaluation inside the virtual environment
Follow the instructions in README.md in the following five directories to do the evaluation. Training and testing sets for **Single-Aux-Model-Experiments** and **Multiple-Aux-Models-Experiments** are from the same transcription directory (Check README.md inside **Recognition** directory for details). While transcrition directories are organized differently for **Unseen-AE-Attack-Experiments** and **MME-AE-Experiments** (Check README.md files in each directories for details).

1. Single-Aux-Model-Experiments
2. Feature-Generation
   Create similarity scores and feature vectors for multiple-auxiliary-ASRs detection systems.
3. Multiple-Aux-Models-Experiments
4. Unseen-AE-Attack-Experiments
   - Experiment 1: **All AEs** are treated as unseen AEs
   - Experiment 2: **All blackbox AEs** are treated as unseen AEs
   - Experiment 3: **All whitebox AEs** are treated as unseen AEs
5. MME-AE-Experiments
   - First, create hypothetically multiple-ASRs-effective AEs
   - Then, build detection systems using these AEs and real benign samples, and then test them upon unseen hypothetical AEs and real AEs
6. For k-fold validation, please refer to the directory, "k-fold_validation", outside this directory.
7. For the calculation of overhead of the system, DS0+{DS1}, please refer to the directory, "Overhead_Calculation", outside this directory.
