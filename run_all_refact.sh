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

NEW_IMPLEMENTATION=1

RUN_1_CYLINDERS=0
RUN_2_SVC_IVC=0
RUN_3_CUT_VESSELS=0
RUN_4_MYO=0
RUN_5_VALVES=1

if [ $RUN_1_CYLINDERS -eq 1 ] ; then
    echo "===== CREATE CYLINDERS ======"
    python $SCRIPTS_DIR/1_create_cylinders_refact.py $BASE_DIR --points-json $POINTS_JSON --origin-spacing-json $ORIGIN_SPACING_JSON -svc -ivc --seg-name $SEGNAME
fi

if [ $RUN_2_SVC_IVC -eq 1 ] ; then
    echo "===== CREATE SVC/IVC ======"
    python $SCRIPTS_DIR/2_create_svc_ivc_refact.py $BASE_DIR --origin-spacing-json $ORIGIN_SPACING_JSON --seg-name $SEGNAME
fi

if [ $RUN_3_CUT_VESSELS -eq 1  ] ; then
    echo "===== CUT VESSELS ======"
    python $SCRIPTS_DIR/3_cut_vessels_refact.py $BASE_DIR --points-json $POINTS_JSON --seg-name seg_s2a.nrrd --vc-joint-json vc_joint.json --cut-percentage 0.75
fi

if [ $RUN_4_MYO -eq 1 ] ; then
    echo "===== CREATE MYO ======"
    python $SCRIPTS_DIR/4_create_myo_refact.py $BASE_DIR --origin-spacing-json $ORIGIN_SPACING_JSON --points-json $POINTS_JSON 
fi

if [ $RUN_5_VALVES -eq 1 ] ; then
    echo "===== CREATE VALVES ======"
    python $SCRIPTS_DIR/5_create_valve_planes_refact.py $BASE_DIR --origin-spacing-json $ORIGIN_SPACING_JSON --points-json $POINTS_JSON 
fi

