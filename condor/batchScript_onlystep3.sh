#!/usr/bin/env bash

SAMPLE_NAME=${1}
SAMPLE_STEP3=${2}
SAMPLE_ID=${3}

# CLUE3D parameters
CRITICAL_DENSITY=${4}
CRITICAL_ETAPHIDISTANCE=${5}
KERNEL_DENSITY_FACTOR=${6}

STORAGE=/data_CMS/cms/${USER}/${SAMPLE_NAME}
LOC=/grid_mnt/vol_home/llr/cms/${USER}/CMSSW_12_6_0_pre4/src/HGCALprod
FOLDER=${PWD}

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SITECONFIG_PATH=/cvmfs/cms.cern.ch/SITECONF/T2_FR_GRIF_LLR/GRIF-LLR

cd ${loc}
eval $(scram ru -sh)
cd ${FOLDER}

mkdir ${STORAGE}/${SAMPLE_STEP3}

cp ${STORAGE}/step2/step2_${SAMPLE_ID}.root .
mv step2_${SAMPLE_ID}.root step2.root

cp ${loc}/run_Step3andAnalyzer.py .
cmsRun run_Step3andAnalyzer.py isScan=1 \
	   criticalDensity=${CRITICAL_DENSITY} \
	   criticalEtaPhiDistance=${CRITICAL_ETAPHIDISTANCE} \
	   kernelDensityFactor=${KERNEL_DENSITY_FACTOR}

FILE_ID=${SAMPLE_ID}"_CDENS"${CRITICAL_DENSITY/\./p}"_CDIST"${CRITICAL_ETAPHIDISTANCE/\./p}"_KDENS"${KERNEL_DENSITY_FACTOR/\./p}
mv step3.root step3_${FILE_ID}.root
mv step3_${FILE_ID}.root ${STORAGE}/${SAMPLE_STEP3}

cd ${FOLDER}
# rm -f *.py *.cc *.txt *.root
