#!/usr/bin/env bash
set -euo pipefail

if [ $# -eq 0 ] ; then
    >&2 echo 'No arguments supplied'
    exit 1
fi
SCRIPTS_DIR="$(dirname $0)/seg_scripts"

BASE_DIR=$1
SEGNAME="seg_corrected.nrrd"

POINTS_JSON=$BASE_DIR/points.json
ORIGIN_SPACING_JSON=$BASE_DIR/origin_spacing.json

RUN_1_CYLINDERS=0
RUN_2_SVC_IVC=0
RUN_3_SLICERS=0
RUN_4_CROP=0
RUN_5_MYO=0
RUN_6_VALVES=0
RUN_7_CLEAN=0

if [ $# -ge 2 ] ; then
    FUNCTION_NUM=$2
    if ! [[ "$FUNCTION_NUM" =~ ^[1-7]$ ]] ; then
        >&2 echo 'Second argument must be a number between 1 and 7'
        exit 1
    fi
    case $FUNCTION_NUM in
        1) RUN_1_CYLINDERS=1 ;;
        2) RUN_2_SVC_IVC=1 ;;
        3) RUN_3_SLICERS=1 ;;
        4) RUN_4_CROP=1 ;;
        5) RUN_5_MYO=1 ;;
        6) RUN_6_VALVES=1 ;;
        7) RUN_7_CLEAN=1 ;;
    esac
fi

if [ $RUN_1_CYLINDERS -eq 1 ] ; then
    echo "===== CREATE CYLINDERS ======"
    python $SCRIPTS_DIR/1_create_cylinders_refact.py $BASE_DIR --points-json $POINTS_JSON --origin-spacing-json $ORIGIN_SPACING_JSON -svc -ivc --seg-name $SEGNAME
fi

if [ $RUN_2_SVC_IVC -eq 1 ] ; then
    echo "===== CREATE SVC/IVC ======"
    python $SCRIPTS_DIR/2_create_svc_ivc_refact.py $BASE_DIR --origin-spacing-json $ORIGIN_SPACING_JSON --seg-name $SEGNAME
fi

if [ $RUN_3_SLICERS -eq 1  ] ; then
    echo "===== CREATE SLICERS ======"
    python $SCRIPTS_DIR/create_slicers.py $BASE_DIR --points-json $POINTS_JSON --origin-spacing-json $ORIGIN_SPACING_JSON --seg-name seg_s2a.nrrd
fi

if [ $RUN_4_CROP -eq 1 ] ; then
    echo "===== CROP ======"
    python $SCRIPTS_DIR/crop_svc_ivc.py $BASE_DIR --origin-spacing-json $ORIGIN_SPACING_JSON --points-json $POINTS_JSON 
fi

if [ $RUN_5_MYO -eq 1 ] ; then
    echo "===== CREATE MYO ======"
    python $SCRIPTS_DIR/4_create_myo_refact.py $BASE_DIR --origin-spacing-json $ORIGIN_SPACING_JSON --points-json $POINTS_JSON 
fi

if [ $RUN_6_VALVES -eq 1 ] ; then
    echo "===== CREATE VALVES ======"
    python $SCRIPTS_DIR/5_create_valve_planes_refact.py $BASE_DIR --origin-spacing-json $ORIGIN_SPACING_JSON --points-json $POINTS_JSON 
fi

if [ $RUN_7_CLEAN -eq 1 ] ; then
    echo "===== CLEAN SEGMENTATION ======"
    python $SCRIPTS_DIR/6_clean_seg_refact.py $BASE_DIR --points-json $POINTS_JSON --origin-spacing-json $ORIGIN_SPACING_JSON
fi



