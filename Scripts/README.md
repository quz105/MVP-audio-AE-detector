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
Follow the instructions in README.md in the following four directories to do the evaluation. 

1. k-fold_validation
2. Unseen-AE-Attack-Experiments
   - Experiment 1: **All AEs** are treated as unseen AEs
   - Experiment 2: **All blackbox AEs** are treated as unseen AEs
   - Experiment 3: **All whitebox AEs** are treated as unseen AEs
3. MME-AE-Experiments
   - First, create hypothetically multiple-ASRs-effective AEs
   - Then, build detection systems using these AEs and real benign samples, and then test them upon unseen hypothetical AEs and real AEs
4. To calculate the overhead of the system, DS0+{DS1}, please refer to the directory, "Overhead_Calculation".
