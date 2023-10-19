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

# convert "mVALpVAL" format to "-VAL.VAL" format
function toFloat() {
	AVAR=${1/p/\.}
	echo ${AVAR/m/\-}
}

CRITICAL_DENSITY_FLOAT=$(toFloat ${4})
CRITICAL_ETAPHIDISTANCE_FLOAT=$(toFloat ${5})
KERNEL_DENSITY_FACTOR_FLOAT=$(toFloat ${6})

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SITECONFIG_PATH=/cvmfs/cms.cern.ch/SITECONF/T2_FR_GRIF_LLR/GRIF-LLR

cd ${LOC}
eval $(scram ru -sh)
cd ${FOLDER}

mkdir ${STORAGE}/${SAMPLE_STEP3}

FILE_ID=${SAMPLE_ID}"_CDENS"${CRITICAL_DENSITY}"_CDIST"${CRITICAL_ETAPHIDISTANCE}"_KDENS"${KERNEL_DENSITY_FACTOR}
FILE_STEP3="step3_${FILE_ID}.root"

cp ${LOC}/run_Step3andAnalyzer.py .
cmsRun run_Step3andAnalyzer.py isScan=1 \
	   step2File="${STORAGE}/step2/step2_${SAMPLE_ID}.root" \
	   step3File=${FILE_STEP3} \
	   criticalDensity=${CRITICAL_DENSITY_FLOAT} \
	   criticalEtaPhiDistance=${CRITICAL_ETAPHIDISTANCE_FLOAT} \
	   kernelDensityFactor=${KERNEL_DENSITY_FACTOR_FLOAT}

if [ -f ${FILE_STEP3} ]; then
	mv ${FILE_STEP3} ${STORAGE}/${SAMPLE_STEP3}/${FILE_STEP3}
else
	echo "File ${FILE_STEP3} not found!"
fi

# cd ${FOLDER}
# rm -f *.py *.cc *.txt *.root
