#!/usr/bin/env bash

SAMPLE_NAME=${1}
SAMPLE_STEP3=${2}
SAMPLE_ID=${3}
TAG=${4}

# CLUE3D parameters
CRITICAL_DENSITY=${5}
CRITICAL_ETAPHIDISTANCE=${6}
KERNEL_DENSITY_FACTOR=${7}

STORAGE=/data_CMS/cms/${USER}/${SAMPLE_NAME}
LOC=/grid_mnt/vol_home/llr/cms/${USER}/CMSSW_12_6_0_pre4/src/HGCALprod
FOLDER=${PWD}

# convert "mVALpVAL" format to "-VAL.VAL" format
function toFloat() {
	AVAR=${1/p/\.}
	echo ${AVAR/m/\-}
}

CRITICAL_DENSITY_FLOAT=$(toFloat ${CRITICAL_DENSITY})
CRITICAL_ETAPHIDISTANCE_FLOAT=$(toFloat ${CRITICAL_ETAPHIDISTANCE})
KERNEL_DENSITY_FACTOR_FLOAT=$(toFloat ${KERNEL_DENSITY_FACTOR})

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SITECONFIG_PATH=/cvmfs/cms.cern.ch/SITECONF/T2_FR_GRIF_LLR/GRIF-LLR

cd ${LOC}
eval $(scram ru -sh)
cd ${FOLDER}

mkdir ${STORAGE}/${SAMPLE_STEP3}

FILE_ID=${SAMPLE_ID}"_CDENS"${CRITICAL_DENSITY}"_CDIST"${CRITICAL_ETAPHIDISTANCE}"_KDENS"${KERNEL_DENSITY_FACTOR}
FILE_STEP3="step3_${FILE_ID}${TAG}.root"

cp ${LOC}/run_Step3andAnalyzer.py .
# example:
# cmsRun run_Step3andAnalyzer.py isScan=1 step2File=/data_CMS/cms/alves/SinglePion_0PU_10En200_CEH_16Jul//step2/step2_22.root step3File=step3.root criticalDensity=0.6 criticalEtaPhiDistance=1.0 kernelDensityFactor=2.0
cmsRun run_Step3andAnalyzer.py isScan=1 \
	   step2File=${STORAGE}/step2/step2_${SAMPLE_ID}.root \
	   step3File=${FILE_STEP3} \
	   criticalDensity=${CRITICAL_DENSITY_FLOAT} \
	   criticalEtaPhiDistance=${CRITICAL_ETAPHIDISTANCE_FLOAT} \
	   kernelDensityFactor=${KERNEL_DENSITY_FACTOR_FLOAT}

if [ -f ${FILE_STEP3} ]; then
	mv ${FILE_STEP3} ${STORAGE}/${SAMPLE_STEP3}/${FILE_STEP3}
	echo "File ${FILE_STEP3} moved to ${STORAGE}/${SAMPLE_STEP3}."
else
	echo "File ${FILE_STEP3} not found!"
fi
