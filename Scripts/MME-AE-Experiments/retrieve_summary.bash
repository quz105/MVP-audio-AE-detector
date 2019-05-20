#!/bin/bash 

RESULT_DIR=$1

echo -e "==Experimental Result on Testing dataset For Each Type of MAE AEs=="
echo -e "[MME_AE_DS0_DS1]\t" $(cat "$RESULT_DIR"/MME_AE_DS0_DS1/result_MME_AE_DS0_DS1.txt)
echo -e "[MME_AE_DS0_GCS]\t" $(cat "$RESULT_DIR"/MME_AE_DS0_GCS/result_MME_AE_DS0_GCS.txt)
echo -e "[MME_AE_DS0_AT]\t\t" $(cat "$RESULT_DIR"/MME_AE_DS0_AT/result_MME_AE_DS0_AT.txt)
echo -e "[MME_AE_DS0_DS1_GCS]\t" $(cat "$RESULT_DIR"/MME_AE_DS0_DS1_GCS/result_MME_AE_DS0_DS1_GCS.txt) 
echo -e "[MME_AE_DS0_DS1_AT]\t" $(cat "$RESULT_DIR"/MME_AE_DS0_DS1_AT/result_MME_AE_DS0_DS1_AT.txt)
echo -e "[MME_AE_DS0_GCS_AT]\t" $(cat "$RESULT_DIR"/MME_AE_DS0_GCS_AT/result_MME_AE_DS0_GCS_AT.txt) 
echo -e "[Comprehensive AE]\t" $(cat "$RESULT_DIR"/Comprehensive_AE/result_Comprehensive_AE.txt)
echo

echo -e "==Testing Each Detection System With Real AEs=="
echo -e "[MME_AE_DS0_AT]\t\t" $(cat "$RESULT_DIR"/MME_AE_DS0_AT/result_testing_unusedAE_SME_AE_DS0.txt)
echo -e "[MME_AE_DS0_GCS]\t"  $(cat "$RESULT_DIR"/MME_AE_DS0_GCS/result_testing_unusedAE_SME_AE_DS0.txt)
echo -e "[MME_AE_DS0_DS1]\t"  $(cat "$RESULT_DIR"/MME_AE_DS0_DS1/result_testing_unusedAE_SME_AE_DS0.txt)
echo -e "[MME_AE_DS0_DS1_GCS]\t"  $(cat "$RESULT_DIR"/MME_AE_DS0_DS1_GCS/result_testing_unusedAE_SME_AE_DS0.txt)
echo -e "[MME_AE_DS0_DS1_AT]\t"  $(cat "$RESULT_DIR"/MME_AE_DS0_DS1_AT/result_testing_unusedAE_SME_AE_DS0.txt)
echo -e "[MME_AE_DS0_GCS_AT]\t"  $(cat "$RESULT_DIR"/MME_AE_DS0_GCS_AT/result_testing_unusedAE_SME_AE_DS0.txt)
echo -e "[Comprehensive_AE]\t"  $(cat "$RESULT_DIR"/Comprehensive_AE/result_testing_unusedAE_SME_AE_DS0.txt)
echo

echo -e "==Testing Detector~>{DS0, DS1, GCS} with AE(DS0, DS1) and AE(DS0, GCS)=="
echo -e "[AE(DS0, DS1)]\t" $(cat "$RESULT_DIR"/MME_AE_DS0_DS1_GCS/result_testing_unusedAE_MME_AE_DS0_DS1.txt)
echo -e "[AE(DS0, GCS)]\t" $(cat "$RESULT_DIR"/MME_AE_DS0_DS1_GCS/result_testing_unusedAE_MME_AE_DS0_GCS.txt)
echo

echo -e "==Testing Detector~>{DS0, DS1, AT} with AE(DS0, DS1) and AE(DS0, AT)=="
echo -e "[AE(DS0, DS1)]\t" $(cat "$RESULT_DIR"/MME_AE_DS0_DS1_AT/result_testing_unusedAE_MME_AE_DS0_DS1.txt)
echo -e "[AE(DS0, AT)]\t" $(cat "$RESULT_DIR"/MME_AE_DS0_DS1_AT/result_testing_unusedAE_MME_AE_DS0_AT.txt)
echo

echo -e "==Testing Detector~>{DS0, GCS, AT} with AE(DS0, GCS) and AE(DS0, AT)=="
echo -e "[AE(DS0, GCS)]\t" $(cat "$RESULT_DIR"/MME_AE_DS0_GCS_AT/result_testing_unusedAE_MME_AE_DS0_GCS.txt)
echo -e "[AE(DS0, AT)]\t" $(cat "$RESULT_DIR"/MME_AE_DS0_GCS_AT/result_testing_unusedAE_MME_AE_DS0_AT.txt)
echo

echo -e "==Testing Detector built upon Comprehensive AEs with Real AE, AE(DS0, DS1), AE(DS0, GCS) and AE(DS0, AT)=="
echo -e "[Real AE]\t" $(cat "$RESULT_DIR"/Comprehensive_AE/result_testing_unusedAE_SME_AE_DS0.txt)
echo -e "[AE(DS0, DS1)]\t" $(cat "$RESULT_DIR"/Comprehensive_AE/result_testing_unusedAE_MME_AE_DS0_DS1.txt) 
echo -e "[AE(DS0, GCS)]\t" $(cat "$RESULT_DIR"/Comprehensive_AE/result_testing_unusedAE_MME_AE_DS0_GCS.txt)
echo -e "[AE(DS0, AT)]\t" $(cat "$RESULT_DIR"/Comprehensive_AE/result_testing_unusedAE_MME_AE_DS0_AT.txt)
